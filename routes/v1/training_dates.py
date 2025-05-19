import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, Body

from models.response import SuccessResponse, TrainingDateListResponse
from models.training_date import TrainingDateBase, TrainingDateDB, TrainingDateUpdate
from utils.config import settings
from utils.database import training_dates_collection, trainings_collection, bookings_collection
from utils.helper import get_current_user, convert_objectid_to_str
from utils.permissions import check_permission

router = APIRouter(prefix="/training-dates", tags=["Training Dates"], dependencies=[])


@router.get("/", response_model=TrainingDateListResponse)
async def get_training_dates(
        id: str = Query(None, description="Filter by id"),
        training_id: str = Query(None, description="Filter by training id"),
        limit: int = Query(settings.DEFAULT_GET_LIMIT, ge=1, le=settings.MAX_GET_LIMIT,
                           description="Limit the number of results")
):
    """
    Get a list of all training dates, optionally filtered by training_id.
    """
    query = {}
    if id:
        query["_id"] = ObjectId(id)
    if training_id:
        query["training_id"] = training_id

    training_dates = await training_dates_collection.find(query).to_list(length=limit)
    for date in training_dates:
        date["id"] = convert_objectid_to_str(date["_id"])
        del date["_id"]

    return {"status": True, "data": training_dates}


@router.post("/", response_model=SuccessResponse, dependencies=[Depends(get_current_user), Depends(check_permission("create"))])
async def create_training_date(training_date: TrainingDateBase, user=Depends(get_current_user)):
    """
    Create a new training date.
    """
    # Check if the training exists
    try:
        id = ObjectId(training_date.training_id)
    except:
        raise HTTPException(status_code=404, detail="Training id is not valid")
    training = await trainings_collection.find_one({"_id": id})
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")

    # Validate dates
    if training_date.start_date >= training_date.end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")

    # Check if the available slots is valid
    if training_date.available_slots > training["max_participants"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Available slots cannot exceed maximum participants ({training['max_participants']})"
        )

    training_date_dict = training_date.model_dump()
    training_date_dict["created_by"] = user.id
    training_date_dict["created_at"] = datetime.datetime.now(datetime.UTC)

    training_date_db = TrainingDateDB(**training_date_dict)
    result = await training_dates_collection.insert_one(training_date_db.model_dump(exclude_none=True))

    return {"status": True, "message": "Training date created successfully", "id": str(result.inserted_id)}


@router.put("/", response_model=SuccessResponse, dependencies=[Depends(get_current_user), Depends(check_permission("update"))])
async def update_training_date(training_date_data: TrainingDateUpdate = Body(...), user=Depends(get_current_user)):
    """
    Update an existing training date.
    """
    # Check if the training date exists
    existing = await training_dates_collection.find_one({"_id": ObjectId(training_date_data.id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Training date not found")

    # Check if the user is allowed to update this training date
    if existing["created_by"] != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to update this training date")

    # Check if the training exists if training_id is provided
    if training_date_data.training_id:
        training = await trainings_collection.find_one({"_id": ObjectId(training_date_data.training_id)})
        if not training:
            raise HTTPException(status_code=404, detail="Training not found")

    # Validate dates if both are provided
    if training_date_data.start_date and training_date_data.end_date:
        if training_date_data.start_date >= training_date_data.end_date:
            raise HTTPException(status_code=400, detail="Start date must be before end date")

    # Check if the available slots is valid
    if training_date_data.available_slots is not None:
        # Get the training to check max_participants
        training_id = training_date_data.training_id or existing["training_id"]
        training = await trainings_collection.find_one({"_id": ObjectId(training_id)})
        if training_date_data.available_slots > training["max_participants"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Available slots cannot exceed maximum participants ({training['max_participants']})"
            )

        # Check if there are already bookings for this date
        bookings_count = await bookings_collection.count_documents({"training_date_id": training_date_data.id})
        if bookings_count > training_date_data.available_slots:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot reduce available slots below current bookings count ({bookings_count})"
            )

    update_data = training_date_data.model_dump(exclude={"id", "created_by"}, exclude_none=True)

    result = await training_dates_collection.update_one(
        {"_id": ObjectId(training_date_data.id)},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Training date not found or no change detected")

    return {"status": True, "message": "Training date updated successfully", "id": training_date_data.id}


@router.delete("/{id}", response_model=SuccessResponse, dependencies=[Depends(get_current_user), Depends(check_permission("delete"))])
async def delete_training_date(id: str, user=Depends(get_current_user)):
    """
    Delete a training date.
    """
    # Check if the training date exists
    existing = await training_dates_collection.find_one({"_id": ObjectId(id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Training date not found")

    # Check if the user is allowed to delete this training date
    if existing["created_by"] != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this training date")

    # Check if there are any bookings for this training date
    bookings = await bookings_collection.find_one({"training_date_id": id})
    if bookings:
        raise HTTPException(status_code=400, detail="Cannot delete training date with associated bookings")

    result = await training_dates_collection.delete_one({"_id": ObjectId(id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Training date not found")

    return {"status": True, "message": "Training date deleted successfully"}
