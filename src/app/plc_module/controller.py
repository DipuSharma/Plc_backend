from src.config.mongo_db import devices_collection, plc_collection

async def get_plc_data(plc_name: str):
    result = await devices_collection.find_one({"plc": plc_name})
    return result["data"]


def get_all_plcs():
    """
    Fetch all active PLC connection details from MongoDB.
    """
    return list(plc_collection.find({"status": "active"}))