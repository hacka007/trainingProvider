from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class TrainingBase(BaseModel):
    name: str
    description: str
    price: float
    instructor: str
    duration_hours: float = Field(gt=0)
    max_participants: int = Field(default=10, ge=1)

    def to_mongo(self) -> dict:
        return self.model_dump(by_alias=True)


class TrainingDB(TrainingBase):
    created_at: datetime
    created_by: str

    def dict_without_none(self):
        """Return a dictionary excluding None values."""
        return {
            key: (value.isoformat() if isinstance(value, datetime) else value)
            for key, value in self.dict().items()
            if value is not None
        }

    model_config = ConfigDict(extra="forbid")


class TrainingResponse(TrainingDB):
    id: str


class TrainingUpdate(TrainingBase):
    id: str
