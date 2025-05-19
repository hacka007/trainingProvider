from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, ConfigDict


# User Models
class RoleBase(BaseModel):
    name: str
    permissions: List[str]


class RoleDB(RoleBase):
    id: str = Field(default_factory=str, alias="_id")
    name: str
    permissions: List[str]

    def dict_without_none(self):
        """Return a dictionary excluding None values."""
        return {
            key: (value.isoformat() if isinstance(value, datetime) else value)
            for key, value in self.dict().items()
            if value is not None
        }

    model_config = ConfigDict(extra="forbid")
