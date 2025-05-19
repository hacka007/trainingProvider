from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class TrainingDateBase(BaseModel):
    training_id: str
    start_date: datetime
    end_date: datetime
    location: str
    available_slots: int = Field(default=10, ge=0)

    def to_mongo(self) -> dict:
        return self.model_dump(by_alias=True)


class TrainingDateDB(TrainingDateBase):
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


class TrainingDateResponse(TrainingDateDB):
    id: str


class TrainingDateUpdate(TrainingDateBase):
    id: str
    created_by: str
