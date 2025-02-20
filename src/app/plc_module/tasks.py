import asyncio
from src.worker.celery_worker import celery_app
from datetime import datetime
from src.config.mongo_db import message_collection, plc_collection


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
    plcs = await plc_collection.find({}, {"plc_id": 1}).to_list(length=None)  # ✅ Await this!
    
    for plc in plcs:
        plc_id = plc["plc_id"]
        message = await message_collection.find_one({"plc_id": plc_id}, {"message": 1})  # ✅ Await this!
        if message:
            process_plc_message.delay(plc_id, message["message"])  # ✅ Use Celery's .delay()