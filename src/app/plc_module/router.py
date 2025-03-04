from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel, Field
from src.app.plc_module import controller as plc_controller
from src.config.mongo_db import plc_collection
from src.app.plc_module.schema import PlcCreateSchema, PlcUpdateSchema, FilterSchema, PlcCommandSchema

router = APIRouter()


  

@router.post('/add-plc')
async def add_plc(payload: PlcCreateSchema):
    result, message = await plc_controller.add_plc(payload)
    return {"message": message, "result": result if result else None}



@router.put('/update-plc/{plc_id}')
async def update_plc(plc_id: str, payload: PlcUpdateSchema):
    result, message = await plc_controller.plc_update_by_id(plc_collection,plc_id, payload)
    return {"message": message, "result": result if result else None}


@router.delete('/delete-plc/{plc_id}')
async def delete_plc(plc_id: str):
    result, message = await plc_controller.delete_plc_data(plc_id)
    return {"message": message, "result": result if result else None}


@router.get('/get-all-plcs')
async def get_all(request: Request, filter: FilterSchema = Depends()):
    result = await plc_controller.get_list(request=request,**filter.dict())
    return {"data": result if result else []}


@router.post('/send-command')
async def send_command(payload: PlcCommandSchema):
    result, message = await plc_controller.send_command_to_plc(payload.plc_id, payload.command, payload.value)
    if not result:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "result": result}