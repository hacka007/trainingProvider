from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from models.user import UserDB
from utils.config import settings
from utils.database import users_collection

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")


def convert_objectid_to_str(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: str(v) if isinstance(v, ObjectId) else convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    return data


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        user = convert_objectid_to_str(user)
        user["id"] = user["_id"]
        del user["_id"]
        return UserDB(**user)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

