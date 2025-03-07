import asyncio
from src.worker.celery_worker import celery_app
from datetime import datetime
from src.config.mongo_db import message_collection, plc_collection, iothub_device_collection
from pymodbus.client import ModbusTcpClient
# executor = ThreadPoolExecutor()

@celery_app.task(bind=True)
def process_plc_message(plc_id, message):
    print(f"Processing PLC ({plc_id}) message: {message}")
    message_collection.update_one(
        {"plc_id": plc_id}, 
        {"$set": {"last_message": message, "timestamp": datetime.datetime.utcnow()}}, 
        upsert=True
    )

@celery_app.task(bind=True)
def fetch_plc_messages(self):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.run(fetch_data())
    else:
        loop.run_until_complete(fetch_data())

async def fetch_data():
    plcs = await plc_collection.find({}, {"plc_id": 1}).to_list(length=None)
    for plc in plcs:
        plc_id = plc["plc_id"]
        message = await message_collection.find_one({"plc_id": plc_id}, {"message": 1})
        if message:
            process_plc_message.delay(plc_id, message["message"])

@celery_app.task
def fetch_all_plc_messages():
    """ Fetch data from all PLCs asynchronously every second """

    async def fetch_and_store():
        try:
            # Fetch PLC configurations from MongoDB
            plcs = await plc_collection.find({}, {"plc_id": 1, "ip_address": 1, "port": 1}).to_list(length=100)
            if not plcs:
                print("Not plc device found")
            for plc in plcs:
                plc_id = plc["plc_id"]
                plc_ip = plc["ip_address"]
                plc_port = plc["port"]

                try:
                    # Connect to PLC
                    plc_client = ModbusTcpClient(plc_ip, port=plc_port)
                    plc_client.connect()
                    response = plc_client.read_holding_registers(0, 2)  # Adjust based on PLC setup

                    if not response.isError():
                        data = {
                            "plc_id": plc_id,
                            "timestamp": datetime.datetime.utcnow(),
                            "register_0": response.registers[0],
                            "register_1": response.registers[1],
                            "processed": True
                        }
                        await message_collection.insert_one(data)  # Store in MongoDB
                        print(f"Stored Data: {data}")

                except Exception as e:
                    print(f"Error fetching from {plc_id}: {e}")

                finally:
                    plc_client.close()  # Ensure connection is closed

        except Exception as e:
            print(f"Database error: {e}")

    # Run async function inside a thread pool
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(fetch_and_store())

    return "Fetched data from all PLCs"

@celery_app.task
async def receive_message():
    """ Receives messages from all devices every 5 seconds """
    plcs = await iothub_device_collection.find().to_list(length=100)
    if not plcs:
        print("Not plc device found")
    for item in plcs:
        try:
            client = IoTHubDeviceClient.create_from_connection_string(item.conn_str)
            client.connect()

            message = client.receive_message()  # Blocking call
            if message:
                message_data = message.data.decode("utf-8")
                print(f"Received from {item.device_id}: {message_data}")

                # Store in MongoDB
                collection.insert_one({
                    "device_id": item.device_id,
                    "message": message_data,
                    "timestamp": datetime.utcnow()
                })
            
            client.disconnect()
        
        except Exception as e:
            print(f"Error receiving message from {item.device_id}: {str(e)}")