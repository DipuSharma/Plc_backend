import asyncio
import logging
from datetime import datetime
from azure.iot.device.aio import IoTHubDeviceClient
from src.worker.celery_worker import celery_app
from src.config.mongo_db import message_collection, iothub_device_collection

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------- RECEIVE MESSAGES FROM IOT HUB ----------------------
@celery_app.task
def receive_message():
    """Receives messages from all IoT devices asynchronously"""
    asyncio.run(receive_message_async())  # Safe execution within Celery

async def receive_message_async():
    """ Asynchronously fetches messages from IoT Hub for multiple devices """
    try:
        plcs = await iothub_device_collection.find().to_list(length=100)
        if not plcs:
            logger.info("No IoT devices found in the database.")
            return
        await asyncio.gather(*[handle_iot_message(item) for item in plcs])
    except Exception as e:
        logger.error(f"Error fetching IoT device list: {e}")

async def handle_iot_message(item):
    """Handles receiving messages from an IoT Hub device"""
    client = None
    try:
        logger.info(f"Connecting to IoT device: {item['device_id']}")
        client = IoTHubDeviceClient.create_from_connection_string(item["conn_str"])
        await client.connect()
        message = await client.receive_message()
        if message:
            message_data = message.data.decode("utf-8")
            logger.info(f"Received from {item['device_id']}: {message_data}")
            await message_collection.insert_one({
                "device_id": item["device_id"],
                "message": message_data,
                "timestamp": datetime.utcnow()
            })
    
    except Exception as e:
        logger.error(f"Error receiving message from {item['device_id']}: {e}")

    finally:
        if client:
            await client.disconnect()
            logger.info(f"Disconnected from IoT device: {item['device_id']}")
