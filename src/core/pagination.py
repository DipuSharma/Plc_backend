from typing import Dict, List, Type, TypeVar, Generic, Optional
from pydantic import BaseModel
from pymongo.collection import Collection
import math
from fastapi import Request

ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)


class AsyncPaginator(Generic[ResponseSchemaType]):
    def __init__(
        self,
        collection: Collection,
        schema: Type[ResponseSchemaType],
        request: Request,
        filter: Dict,
        page: int = 1,
        limit: int = 10,
        search_query: Optional[Dict] = None,
    ):
        self.collection = collection
        self.schema = schema
        self.request = request
        self.filter = filter
        self.page = page
        self.limit = limit
        self.search_query = search_query or {}
        self.total_items = 0

    async def get_total_count(self) -> int:
        """Count total items in the collection matching the query."""
        self.total_items = await self.collection.count_documents(self.search_query)
        return self.total_items

    async def get_paginated_results(self) -> Dict:
        """Fetch and paginate results."""
        skip = (self.page - 1) * self.limit
        cursor = self.collection.find(self.search_query).skip(skip).limit(self.limit)

        # results = [self.schema(**doc) async for doc in cursor]
        results = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            results.append(self.schema(**doc))
        if self.total_items == 0:
            await self.get_total_count()
        total_pages = math.ceil(self.total_items / self.limit)
        next_page_url = None
        previous_page_url = None

        if self.page < total_pages:
            next_page_url = self.build_pagination_url(self.page + 1)

        if self.page > 1:
            previous_page_url = self.build_pagination_url(self.page - 1)

        return {
            "result": results,
            "total_items": self.total_items,
            "page": self.page,
            "limit": self.limit,
            "total_pages": total_pages,
            "next_page_url": next_page_url,
            "previous_page_url": previous_page_url,
        }

    def build_pagination_url(self, page: int) -> str:
        """Build pagination URL."""
        url = str(self.request.url).split("?")[0]
        query_params = self.filter.copy()
        query_params["page"] = page
        query_params["limit"] = self.limit
        return (
            f"{url}?{'&'.join(f'{key}={value}' for key, value in query_params.items())}"
        )