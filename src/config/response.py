from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from fastapi import status


class ResponseModel(BaseModel):
    """
    Base Response Model
    """
    data: Any = {}
    status_code: int = status.HTTP_200_OK
    success: bool = True
    message: str = 'Request handled successfully'


class ErrorResponseModel(BaseModel):
    """
    Base Error Model
    """
    error: Any = {}
    status_code: int = status.HTTP_400_BAD_REQUEST
    success: bool = False
    message: str = 'Request could not be processed'


class ExistResponseModel(BaseModel):
    """
    Existing Record Show
    """
    data: Any = {}
    status_code: int = status.HTTP_226_IM_USED
    success: bool = True
    message: str = None

class WebhookResponse(BaseModel):
    result: str


class WebhookRequest(BaseModel):
    type: Optional[str] = Field(description="Type of event being fired")
    data: Optional[Dict] = Field(description="Event data payload")
    created_at: Optional[datetime] = Field(description="Created date and time")
    updated_at: Optional[datetime] = Field(description="Updated date and time")