import datetime
import logging

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, Body

from models.response import SuccessResponse, TrainingListResponse
from models.training import TrainingBase, TrainingDB, TrainingUpdate
from utils.config import settings
from utils.database import trainings_collection, training_dates_collection
from utils.helper import get_current_user, convert_objectid_to_str
from utils.permissions import check_permission

router = APIRouter(prefix="/trainings", tags=["Trainings"], dependencies=[])

logger = logging.getLogger(__name__)


@router.get("/", response_model=TrainingListResponse)
async def get_trainings(
        id: str = Query(None, description="Filter by id"),
        limit: int = Query(settings.DEFAULT_GET_LIMIT, ge=1, le=settings.MAX_GET_LIMIT,
                           description="Limit the number of results")
):
    """
    Get a list of all trainings.
    """
    query = {}
    if id is not None:
        query["_id"] = ObjectId(id)

    trainings = await trainings_collection.find(query).to_list(length=limit)
    for training in trainings:
        training["id"] = convert_objectid_to_str(training["_id"])
        del training["_id"]

    return {"status": True, "data": trainings}


@router.get("/time-period", response_model=TrainingListResponse)
async def get_trainings_by_time_period(
        start_date: datetime.datetime = Query(..., description="Start date for filtering"),
        end_date: datetime.datetime = Query(..., description="End date for filtering"),
        limit: int = Query(settings.DEFAULT_GET_LIMIT, ge=1, le=settings.MAX_GET_LIMIT,
                           description="Limit the number of results")
):
    """
    Get a list of trainings available in a specific time period.
    This endpoint queries training dates and returns the associated trainings.
    """
    # First, find training dates in the specified period
    pipeline = [
        {
            "$match": {
                "start_date": {"$gte": start_date},
                "end_date": {"$lte": end_date}
            }
        },
        {
            "$project": {
                "training_id": 1,
                "training_id_type": {"$type": "$training_id"},
                "start_date": 1,
                "end_date": 1
            }
        },
        {
            "$addFields": {
                "training_id": {
                    "$cond": {
                        "if": {"$eq": [{"$type": "$training_id"}, "string"]},
                        "then": {"$toObjectId": "$training_id"},
                        "else": "$training_id"
                    }
                }
            }
        },
        {
            "$lookup": {
                "from": "trainings",
                "localField": "training_id",
                "foreignField": "_id",
                "as": "training"
            }
        },
        {
            "$project": {
                "training_id": 1,
                "training": 1,
                "training_array_size": {"$size": "$training"}
            }
        },
        {
            "$unwind": {
                "path": "$training",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$replaceRoot": {"newRoot": "$training"}
        },
        {
            "$group": {
                "_id": "$_id",
                "name": {"$first": "$name"},
                "description": {"$first": "$description"},
                "price": {"$first": "$price"},
                "instructor": {"$first": "$instructor"},
                "duration_hours": {"$first": "$duration_hours"},
                "max_participants": {"$first": "$max_participants"},
                "created_at": {"$first": "$created_at"},
                "created_by": {"$first": "$created_by"}
            }
        },
        {
            "$limit": limit
        }
    ]

    trainings = await training_dates_collection.aggregate(pipeline).to_list(length=limit)

    for training in trainings:
        training["id"] = convert_objectid_to_str(training["_id"])
        del training["_id"]

    return {"status": True, "data": trainings}


@router.post("/", response_model=SuccessResponse,
             dependencies=[Depends(get_current_user), Depends(check_permission("create"))])
async def create_training(training: TrainingBase, user=Depends(get_current_user)):
    """
    Create a new training.
    """
    # Check if a training with the same name already exists
    existing = await trainings_collection.find_one({"name": training.name})
    if existing:
        raise HTTPException(status_code=400, detail="Training with this name already exists")

    training_dict = training.model_dump()
    training_dict["created_by"] = user.id
    training_dict["created_at"] = datetime.datetime.now(datetime.UTC)

    training_db = TrainingDB(**training_dict)
    result = await trainings_collection.insert_one(training_db.model_dump(exclude_none=True))

    return {"status": True, "message": "Training created successfully", "id": str(result.inserted_id)}


@router.put("/", response_model=SuccessResponse,
            dependencies=[Depends(get_current_user), Depends(check_permission("update"))])
async def update_training(training_data: TrainingUpdate = Body(...), user=Depends(get_current_user)):
    """
    Update an existing training.
    """
    # Check if the training exists
    existing = await trainings_collection.find_one({"_id": ObjectId(training_data.id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Training not found")

    # Check if the user is allowed to update this training
    if existing["created_by"] != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to update this training")

    update_data = training_data.model_dump(exclude={"id", "created_by"}, exclude_none=True)

    result = await trainings_collection.update_one(
        {"_id": ObjectId(training_data.id)},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Training not found or no change detected")

    return {"status": True, "message": "Training updated successfully", "id": training_data.id}


@router.delete("/{id}", response_model=SuccessResponse,
               dependencies=[Depends(get_current_user), Depends(check_permission("delete"))])
async def delete_training(id: str, user=Depends(get_current_user)):
    """
    Delete a training.
    """
    # Check if the training exists
    existing = await trainings_collection.find_one({"_id": ObjectId(id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Training not found")

    # Check if the user is allowed to delete this training
    if existing["created_by"] != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this training")

    # Check if there are any training dates associated with this training
    training_dates = await training_dates_collection.find_one({"training_id": id})
    if training_dates:
        raise HTTPException(status_code=400, detail="Cannot delete training with associated dates")

    result = await trainings_collection.delete_one({"_id": ObjectId(id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Training not found")

    return {"status": True, "message": "Training deleted successfully"}
