from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BookingBase(BaseModel):
    training_date_id: str
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    notes: Optional[str] = None

    def to_mongo(self) -> dict:
        return self.model_dump(by_alias=True)


class BookingDB(BookingBase):
    created_at: datetime
    created_by: str
    status: str = "confirmed"  # confirmed, cancelled, completed

    def dict_without_none(self):
        """Return a dictionary excluding None values."""
        return {
            key: (value.isoformat() if isinstance(value, datetime) else value)
            for key, value in self.dict().items()
            if value is not None
        }

    model_config = ConfigDict(extra="forbid")


class BookingResponse(BookingDB):
    id: str


class BookingUpdate(BookingBase):
    id: str
    status: Optional[str] = None
