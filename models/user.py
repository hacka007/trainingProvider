from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    password: str
    roles: List[str] = ["user"]
    permissions: List[str] = []

    def to_mongo(self) -> dict:
        return self.model_dump(by_alias=True)


class UserDB(UserBase):
    id: Optional[str] = None
    created_at: datetime

    def dict_without_none(self):
        """Return a dictionary excluding None values."""
        return {
            key: (value.isoformat() if isinstance(value, datetime) else value)
            for key, value in self.dict().items()
            if value is not None
        }

    model_config = ConfigDict(extra="forbid")


class UserResponse(UserDB):
    id: str
    password: str = Field(exclude=True)
