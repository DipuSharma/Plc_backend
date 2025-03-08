from fastapi import HTTPException, status
from src.config.mongo_db import plc_collection, iothub_device_collection, message_collection
from src.app.plc_module.schema import (
    PlcCreateSchema, 
    PlcDeviceShema, 
    PlcUpdateSchema, 
    PlcIotHubCreateSchema, 
    PlcIotHubUpdateSchema, 
    PlcIotHubDeviceSchema,
    PlcMessageSchema
    )
from fastapi.encoders import jsonable_encoder
from pymongo.errors import DuplicateKeyError
from typing import Optional, List, Dict, Union, Tuple   
from datetime import datetime
from src.core.pagination import AsyncPaginator
from pymodbus.client import ModbusTcpClient

class ModbusClient:
    def __init__(self, host: str, port: int = 502):
        self.client = ModbusTcpClient(host, port)

    def connect(self):
        self.client.connect()

    def close(self):
        self.client.close()

    def write_register(self, address: int, value: int):
        """Write a single value to a Modbus register."""
        try:
            if not self.client.connected:
                self.connect()
            response = self.client.write_register(address, value)
            return response.isError() is False, "Write successful" if not response.isError() else str(response)
        except Exception as e:
            return False, f"Error: {str(e)}"

    def read_register(self, address: int, count: int = 1):
        """Read values from a Modbus register."""
        try:
            if not self.client.connected:
                self.connect()
            response = self.client.read_holding_registers(address, count)
            if response.isError():
                return None, str(response)
            return response.registers, "Read successful"
        except Exception as e:
            return None, f"Error: {str(e)}"


async def add_plc(payload: PlcCreateSchema):
    try:
        await  plc_collection.create_index('plc_id', unique=True)
        insert_result = await plc_collection.insert_one(jsonable_encoder(payload))
        if not insert_result.inserted_id:
            return None, "Failed to add PLC"
        created_plc = await plc_collection.find_one({"_id": insert_result.inserted_id})
        if not created_plc:
            return None, "Failed to retrieve added PLC"
        created_plc["id"] = str(created_plc["_id"])
        del created_plc["_id"]

        return PlcDeviceShema(**created_plc), "PLC added successfully"
    except DuplicateKeyError:
            return None, "A plc device with the same unique key already exists."
    except Exception as e:
        print(f"Error in add_plc: {e}")
        return None, "An error occurred"
    
async def add_iot_hub_device(payload: PlcIotHubCreateSchema):
    try:
        await  iothub_collection.create_index('device_id', unique=True)
        insert_result = await iothub_collection.insert_one(jsonable_encoder(payload))
        if not insert_result.inserted_id:
            return None, "Failed to add PLC"
        created_plc = await iothub_collection.find_one({"_id": insert_result.inserted_id})
        if not created_plc:
            return None, "Failed to retrieve added PLC"
        created_plc["id"] = str(created_plc["_id"])
        del created_plc["_id"]

        return PlcIotHubDeviceSchema(**created_plc), "PLC added successfully"
    except DuplicateKeyError:
            return None, "A plc device with the same unique key already exists."
    except Exception as e:
        print(f"Error in add_plc: {e}") 
        return None, "An error occurred"

async def plc_update_by_id(
        collection: plc_collection,
        plc_id: str,
        payload: PlcUpdateSchema,
    ) -> Optional[Tuple[PlcDeviceShema, str]]:
        """
        Update a plc by ID.
        """
        try:
            update_data = {
                k: v for k, v in payload.dict(exclude_unset=True).items() if v
            }
            result = await collection.update_one(
                {"plc_id": plc_id}, {"$set": update_data}
            )

            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="PLC record not found",
                )

            updated_plc = await collection.find_one({"plc_id": plc_id})
            updated_plc["id"] = str(updated_plc["_id"])
            del updated_plc["_id"]
            return PlcDeviceShema(**updated_plc), "Update data successfully"
        except Exception as e:
            return None, str(e)

async def delete_plc_data(plc_id: str):
    try:
        result = await plc_collection.delete_one({"plc_id": plc_id})
        if result:
            return result.deleted_count
        return 0
    except Exception as e:
        print(e)

async def get_list(
        collection=plc_collection,
        is_active: Optional[int] = None,
        skip: Optional[int] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[List[str]] = ["-created_at"],
        fields: Optional[List[str]] = [],
        search: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        is_pagination: bool = True,
        pagination_url: Optional[str] = "",
        request: str = "",
    ) -> Union[List[PlcDeviceShema], Dict]:
    """
    Get PLC List with optional search, pagination, and date filtering
    """
    max_allowed_days = 90
    search_query = {}

    if search:
        search_query = {
            "$or": [
                {"plc_id": {"$regex": search, "$options": "i"}},
            ]
        }

    if from_date and to_date:
        if (to_date - from_date).days > max_allowed_days:
            raise ValueError(f"Date range cannot exceed {max_allowed_days} days.")
        search_query.update(
            {
                "created_at": {
                    "$gte": from_date,
                    "$lte": to_date,
                }
            }
        )

    if is_pagination:
        paginator = AsyncPaginator(
            collection=collection,
            schema=PlcDeviceShema,
            request=request,
            filter={"search": search},
            page=page,
            limit=limit,
            search_query=search_query,
        )
        paginated_result = await paginator.get_paginated_results()

        for record in paginated_result["result"]:
            plc_data = await collection.find_one(
                {"plc_id": record.plc_id}
            )
            if plc_data:
                plc_data["id"] = str(plc_data["_id"])
                del plc_data["_id"]
                record = PlcDeviceShema(**plc_data)

        return paginated_result, "Plc list fetched successfully"

    # Fetch data from MongoDB
    query_cursor = collection.find(search_query)
    if query_cursor is None:  # Handle None case
        return [], "No records found"

    sort_fields = [
        (field[1:], -1) if field.startswith("-") else (field, 1)
        for field in sort_by
    ]
    if sort_fields:
        query_cursor = query_cursor.sort(sort_fields)

    projection = {field: 1 for field in fields} if fields else None
    if projection:
        query_cursor = query_cursor.project(projection)

    records = []
    async for doc in query_cursor:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        records.append(PlcDeviceShema(**doc))

    if not records:  # Handle empty result case
        return [], "No records found"

    # Fetch PLC data for each record
    for i, record in enumerate(records):
        plc_data = await plc_collection.find_one({"plc_id": record.plc_id})
        if plc_data:
            plc_data["id"] = str(plc_data["_id"])
            del plc_data["_id"]
            records[i] = PlcDeviceShema(**plc_data)

    return records, "Plc list fetched successfully"

async def send_command_to_plc(plc_ip: str, register_address: int, value: int):
    """Send a command to the PLC via Modbus."""
    try:
        get_plc = await plc_collection.find_one({"plc_id": plc_ip})
        if not get_plc:
            raise HTTPException(status_code=404, detail="PLC not found")
        modbus = ModbusClient(host=get_plc["ip_address"], port=get_plc["port"])
        success, message = modbus.write_register(register_address, value)
        modbus.close()
        return success, message
    except Exception as e:
        return False, str(e)


async def get_plc_list(
        collection=iothub_device_collection,
        is_active: Optional[int] = None,
        skip: Optional[int] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[List[str]] = ["-created_at"],
        fields: Optional[List[str]] = [],
        search: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        is_pagination: bool = True,
        pagination_url: Optional[str] = "",
        request: str = "",
    ) -> Union[List[PlcIotHubDeviceSchema], Dict]:
    """
    Get PLC List with optional search, pagination, and date filtering
    """
    max_allowed_days = 90
    search_query = {}

    if search:
        search_query = {
            "$or": [
                {"plc_id": {"$regex": search, "$options": "i"}},
            ]
        }

    if from_date and to_date:
        if (to_date - from_date).days > max_allowed_days:
            raise ValueError(f"Date range cannot exceed {max_allowed_days} days.")
        search_query.update(
            {
                "created_at": {
                    "$gte": from_date,
                    "$lte": to_date,
                }
            }
        )

    if is_pagination:
        paginator = AsyncPaginator(
            collection=collection,
            schema=PlcIotHubDeviceSchema,
            request=request,
            filter={"search": search},
            page=page,
            limit=limit,
            search_query=search_query,
        )
        paginated_result = await paginator.get_paginated_results()

        for record in paginated_result["result"]:
            plc_data = await collection.find_one(
                {"plc_id": record.plc_id}
            )
            if plc_data:
                plc_data["id"] = str(plc_data["_id"])
                del plc_data["_id"]
                record = PlcDeviceShema(**plc_data)

        return paginated_result, "Plc list fetched successfully"

    # Fetch data from MongoDB
    query_cursor = collection.find(search_query)
    if query_cursor is None:  # Handle None case
        return [], "No records found"

    sort_fields = [
        (field[1:], -1) if field.startswith("-") else (field, 1)
        for field in sort_by
    ]
    if sort_fields:
        query_cursor = query_cursor.sort(sort_fields)

    projection = {field: 1 for field in fields} if fields else None
    if projection:
        query_cursor = query_cursor.project(projection)

    records = []
    async for doc in query_cursor:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        records.append(PlcIotHubDeviceSchema(**doc))

    if not records:  # Handle empty result case
        return [], "No records found"

    # Fetch PLC data for each record
    for i, record in enumerate(records):
        plc_data = await plc_collection.find_one({"plc_id": record.plc_id})
        if plc_data:
            plc_data["id"] = str(plc_data["_id"])
            del plc_data["_id"]
            records[i] = PlcIotHubDeviceSchema(**plc_data)

    return records, "Plc list fetched successfully"



async def get_message_list(
        collection=message_collection,
        is_active: Optional[int] = None,
        skip: Optional[int] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[List[str]] = ["-created_at"],
        fields: Optional[List[str]] = [],
        search: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        is_pagination: bool = True,
        pagination_url: Optional[str] = "",
        request: str = "",
    ) -> Union[List[PlcMessageSchema], Dict]:
    """
    Get PLC List with optional search, pagination, and date filtering
    """
    max_allowed_days = 90
    search_query = {}

    if search:
        search_query = {
            "$or": [
                {"plc_id": {"$regex": search, "$options": "i"}},
            ]
        }

    if from_date and to_date:
        if (to_date - from_date).days > max_allowed_days:
            raise ValueError(f"Date range cannot exceed {max_allowed_days} days.")
        search_query.update(
            {
                "created_at": {
                    "$gte": from_date,
                    "$lte": to_date,
                }
            }
        )

    if is_pagination:
        paginator = AsyncPaginator(
            collection=collection,
            schema=PlcMessageSchema,
            request=request,
            filter={"search": search},
            page=page,
            limit=limit,
            search_query=search_query,
        )
        paginated_result = await paginator.get_paginated_results()

        for record in paginated_result["result"]:
            plc_data = await collection.find_one(
                {"plc_id": record.plc_id}
            )
            if plc_data:
                plc_data["id"] = str(plc_data["_id"])
                del plc_data["_id"]
                record = PlcMessageSchema(**plc_data)

        return paginated_result, "Plc list fetched successfully"

    # Fetch data from MongoDB
    query_cursor = collection.find(search_query)
    if query_cursor is None:  # Handle None case
        return [], "No records found"

    sort_fields = [
        (field[1:], -1) if field.startswith("-") else (field, 1)
        for field in sort_by
    ]
    if sort_fields:
        query_cursor = query_cursor.sort(sort_fields)

    projection = {field: 1 for field in fields} if fields else None
    if projection:
        query_cursor = query_cursor.project(projection)

    records = []
    async for doc in query_cursor:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        records.append(PlcMessageSchema(**doc))

    if not records:  # Handle empty result case
        return [], "No records found"

    # Fetch PLC data for each record
    for i, record in enumerate(records):
        plc_data = await plc_collection.find_one({"plc_id": record.plc_id})
        if plc_data:
            plc_data["id"] = str(plc_data["_id"])
            del plc_data["_id"]
            records[i] = PlcMessageSchema(**plc_data)

    return records, "Plc messsage fetched successfully"