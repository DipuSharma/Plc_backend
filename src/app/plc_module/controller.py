from fastapi import HTTPException, status
from src.config.mongo_db import plc_collection
from src.app.plc_module.schema import PlcCreateSchema, PlcDeviceShema, PlcUpdateSchema
from fastapi.encoders import jsonable_encoder
from pymongo.errors import DuplicateKeyError
from typing import Optional, List, Dict, Union, Tuple   
from datetime import datetime
from src.core.pagination import AsyncPaginator

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
        collection= plc_collection,
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
                plc_data = await plc_collection.find_one(
                    {"plc_id": record.plc_id}
                )
                if plc_data:
                    plc_data["id"] = str(plc_data["_id"])
                    del plc_data["_id"]
                    record = PlcDeviceShema(**plc_data)
                else:
                    record = {}

            return paginated_result, "Plc list fetched successfully"
        query_cursor = collection.find(search_query)

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
        for record in records:
            plc_data = await plc_collection.find_one(
                {"plc_id": record.plc_id}
            )
            if plc_data:
                record = PlcDeviceShema(**plc_data)
            else:
                record = {}

        return records, "Plc list fetched successfully"