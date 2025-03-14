from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from fastapi import Query

class FilterSchema(BaseModel):
    page: int = Query(1, ge=1, description="Page number, starts from 1")
    limit: int = Query(10, ge=1, le=100, description="Number of items per page")
    search: Optional[str] = Query(description="Search query for PLC", default=None)
    from_date: Optional[datetime] = Query(description="From date for the PLC", default=None)
    to_date: Optional[datetime] = Query(description="To date for the PLC", default=None)
    is_active: Optional[int] = Query(description="Status of the PLC", default=None)
    is_pagination: Optional[bool] = Query(description="Status of the PLC", default=None)
    pagination_url: Optional[str] = Query(description="Status of the PLC", default=None)

class PlcBaseSchema(BaseModel):
    plc_id: Optional[str] = Field(description="Name of the PLC", default="")
    ip_address: Optional[str ]= Field(description="IP address of the PLC", default="")
    port: Optional[int] = Field(description="Port number of the PLC", default=0)
    unit_id: Optional[int] = Field(description="Unit ID of the PLC", default=0)
    status: Optional[str] = Field(description="Status of the PLC", default="active")

    class Config:
        form_model = True

class PlcCreateSchema(PlcBaseSchema):
    class Config:
        form_model = True
        json_schema_extra = {
            "example": {
                "plc_id": "PLC1",
                "ip_address": "192.168.1.1",
                "port": 1024,
                "unit_id": 1,
                "status": "active"
            }
        }

class PlcUpdateSchema(PlcBaseSchema):
    id: Optional[str] = Field(description="ID of the PLC", default="")

    class Config:
        form_model = True
        json_schema_extra = {
            "example": {
                "id": "PLC1",
                "plc_id": "PLC1",
                "ip_address": "192.168.1.1",
                "port": 1024,
                "unit_id": 1,
                "status": "active"
            }
        }

class PlcDeviceShema(PlcBaseSchema):
    class Config:
        form_model = True
        json_schema_extra = {
            "example": {
                "plc_id": "PLC1",
                "ip_address": "192.168.1.1",
                "port": 1024,
                "unit_id": 1,
                "status": "active"
            }
        }

class PlcCommandSchema(BaseModel):
    plc_id: str = Field(default="", title="PLC ID", description="Name of the PLC")
    command: str = Field(default="", title="Command to Send", description="Command to send to the PLC")
    value: int = Field(default=0, title="Value", description="Value to send to the PLC")

    class Config:
        form_model = True
        json_schema_extra = {
            "example": {
                "plc_id": "PLC1",
                "command": "read",
                "value": 0
            }
        }

class PlcIoTHubSchema(BaseModel):
    device_id: str = Field(default="", title="Iot Hub Device ID", description="Iot Hub Device ID")
    iot_hub_primary_access: str = Field(default="", title="Iot Hub Primary Access", description="Iot Hub Primary Access")
    iot_hub_secondary_access: str = Field(default="", title="Iot Hub Secondary Access", description="Iot Hub Secondary Access")

    class Config:
        form_model = True
        json_schema_extra = {
            "example": {
                "device_id": "device_id",
                "iot_hub_primary_access": "primary_access",
                "iot_hub_secondary_access": "secondary_access"
            }
        }

class PlcIotHubCreateSchema(PlcIoTHubSchema):
    pass

class PlcIotHubUpdateSchema(PlcIoTHubSchema):
    pass

class PlcIotHubDeviceSchema(PlcIoTHubSchema):
    id: str = Field(default="", title="Iot Hub Device ID", description="Iot Hub Device ID")

    class Config:
        form_model = True
        json_schema_extra = {
            "example": {
                "device_id": "device_id",
                "iot_hub_primary_access": "primary_access",
                "iot_hub_secondary_access": "secondary_access"
            }
        }

class PlcMessageSchema(BaseModel):
    message_id: str = Field(default="", title="Message ID", description="Message ID")
    message: str = Field(default="", title="Message", description="Message")

    class Config:
        form_model = True
        json_schema_extra = {
            "example": {
                "message_id": "message_id",
                "message": "message"
            }
        }