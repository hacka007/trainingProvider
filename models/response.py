from typing import List, Optional

from pydantic import BaseModel

from models.booking import BookingResponse
from models.training import TrainingResponse
from models.training_date import TrainingDateResponse
from models.user import UserResponse


class UserListResponse(BaseModel):
    status: bool
    data: List[UserResponse]


class TrainingListResponse(BaseModel):
    status: bool
    data: List[TrainingResponse]


class TrainingDateListResponse(BaseModel):
    status: bool
    data: List[TrainingDateResponse]


class BookingListResponse(BaseModel):
    status: bool
    data: List[BookingResponse]


class SuccessResponse(BaseModel):
    status: bool
    message: str
    id: Optional[str] = ''
