from fastapi import APIRouter
from pydantic import BaseModel
from src.app.plc_module.controller import get_plc_data
from src.config.mongo_db import plc_collection

router = APIRouter()

class PlcDeviceShema(BaseModel):
    plc_id: str
    ip_address: str
    port: int
    register: int
    unit_id: int


@router.post('/add-plc')
async def add_plc(payload: PlcDeviceShema):
    try:
        result = await plc_collection.insert_one(payload.dict())
        return {"message": "PLC added successfully"}
    except Exception as e:
        return {"message": f"Error adding PLC: {str(e)}"}



@router.get('/get-all-plcs')
async def get_all_plcs():
    try:
        result = await plc_collection.find({'status': 'active'}).to_list()
        return {"data": result}
    except Exception as e:
        return {"message": f"Error getting PLCs: {str(e)}"}
