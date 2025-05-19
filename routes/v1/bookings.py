import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, Body

from models.booking import BookingDB, BookingUpdate, BookingBase
from models.response import SuccessResponse, BookingListResponse
from utils.config import settings
from utils.database import bookings_collection, training_dates_collection
from utils.helper import get_current_user, convert_objectid_to_str
from utils.permissions import check_permission

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get("/", response_model=BookingListResponse, dependencies=[Depends(check_permission("manage_booking"))])
async def get_bookings(
        id: str = Query(None, description="Filter by id"),
        training_date_id: str = Query(None, description="Filter by training date id"),
        customer_email: str = Query(None, description="Filter by customer email"),
        limit: int = Query(settings.DEFAULT_GET_LIMIT, ge=1, le=settings.MAX_GET_LIMIT,
                           description="Limit the number of results"),
        user=Depends(get_current_user)
):
    """
    Get a list of all bookings, optionally filtered by training_date_id or customer_email.
    Admin users can see all bookings, regular users can only see their own bookings.
    """
    query = {}
    if id:
        query["_id"] = ObjectId(id)
    if training_date_id:
        query["training_date_id"] = training_date_id
    if customer_email:
        query["customer_email"] = customer_email

    # Regular users can only see their own bookings
    if "admin" not in user.roles:
        query["customer_email"] = user.email

    bookings = await bookings_collection.find(query).to_list(length=limit)
    for booking in bookings:
        booking["id"] = convert_objectid_to_str(booking["_id"])
        del booking["_id"]


    return {"status": True, "data": bookings}


@router.post("/", response_model=SuccessResponse, dependencies=[Depends(check_permission("manage_booking"))])
async def create_booking(booking: BookingBase, user=Depends(get_current_user)):
    """
    Create a new booking. This endpoint requires authentication and the 'manage_booking' permission.
    """
    # Check if the training date exists
    training_date = await training_dates_collection.find_one({"_id": ObjectId(booking.training_date_id)})
    if not training_date:
        raise HTTPException(status_code=404, detail="Training date not found")

    # Check if there are available slots
    if training_date["available_slots"] <= 0:
        raise HTTPException(status_code=400, detail="No available slots for this training date")

    # Check if the customer already has a booking for this training date
    existing = await bookings_collection.find_one({
        "training_date_id": booking.training_date_id,
        "customer_email": booking.customer_email
    })
    if existing:
        raise HTTPException(status_code=400, detail="You already have a booking for this training date")

    booking_dict = booking.model_dump()
    booking_dict["created_at"] = datetime.datetime.now(datetime.UTC)
    booking_dict["created_by"] = user.id

    booking_db = BookingDB(**booking_dict)
    result = await bookings_collection.insert_one(booking_db.model_dump(exclude_none=True))

    # Update available slots in training date
    await training_dates_collection.update_one(
        {"_id": ObjectId(booking.training_date_id)},
        {"$inc": {"available_slots": -1}}
    )

    return {"status": True, "message": "Booking created successfully", "id": str(result.inserted_id)}


@router.put("/", response_model=SuccessResponse, dependencies=[Depends(check_permission("manage_booking"))])
async def update_booking(booking_data: BookingUpdate = Body(...), user=Depends(get_current_user)):
    """
    Update an existing booking. Admin users can update any booking, regular users can only update their own bookings.
    """
    # Check if the booking exists
    existing = await bookings_collection.find_one({"_id": ObjectId(booking_data.id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Regular users can only update their own bookings
    if "admin" not in user.roles and existing["customer_email"] != user.email:
        raise HTTPException(status_code=403, detail="Not allowed to update this booking")

    # If changing training_date_id, check if the new training date exists and has available slots
    if booking_data.training_date_id and booking_data.training_date_id != existing["training_date_id"]:
        new_training_date = await training_dates_collection.find_one({"_id": ObjectId(booking_data.training_date_id)})
        if not new_training_date:
            raise HTTPException(status_code=404, detail="Training date not found")

        if new_training_date["available_slots"] <= 0:
            raise HTTPException(status_code=400, detail="No available slots for this training date")

        # Check if the customer already has a booking for the new training date
        duplicate = await bookings_collection.find_one({
            "training_date_id": booking_data.training_date_id,
            "customer_email": booking_data.customer_email or existing["customer_email"],
            "_id": {"$ne": ObjectId(booking_data.id)}
        })
        if duplicate:
            raise HTTPException(status_code=400, detail="You already have a booking for this training date")

        # Update available slots in both old and new training dates
        await training_dates_collection.update_one(
            {"_id": ObjectId(existing["training_date_id"])},
            {"$inc": {"available_slots": 1}}
        )
        await training_dates_collection.update_one(
            {"_id": ObjectId(booking_data.training_date_id)},
            {"$inc": {"available_slots": -1}}
        )

    update_data = booking_data.model_dump(exclude={"id"}, exclude_none=True)

    result = await bookings_collection.update_one(
        {"_id": ObjectId(booking_data.id)},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found or no change detected")

    return {"status": True, "message": "Booking updated successfully", "id": booking_data.id}


@router.delete("/{id}", response_model=SuccessResponse, dependencies=[Depends(check_permission("manage_booking"))])
async def delete_booking(id: str, user=Depends(get_current_user)):
    """
    Delete a booking. Admin users can delete any booking, regular users can only delete their own bookings.
    """
    # Check if the booking exists
    existing = await bookings_collection.find_one({"_id": ObjectId(id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Regular users can only delete their own bookings
    if "admin" not in user.roles and existing["customer_email"] != user.email:
        raise HTTPException(status_code=403, detail="Not allowed to delete this booking")

    result = await bookings_collection.delete_one({"_id": ObjectId(id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Update available slots in training date
    await training_dates_collection.update_one(
        {"_id": ObjectId(existing["training_date_id"])},
        {"$inc": {"available_slots": 1}}
    )

    return {"status": True, "message": "Booking deleted successfully"}
