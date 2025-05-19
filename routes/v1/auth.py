import datetime
from datetime import timedelta

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import APIKeyHeader, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext

from limiter import limiter
from models.response import UserListResponse
from models.token import Token
from models.user import UserDB, UserBase
from utils.config import settings
from utils.database import users_collection, tokens_collection
from utils.helper import convert_objectid_to_str, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


@router.post("/register")
@limiter.limit("1/second")
async def register(user: UserBase, request: Request):
    if await users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(user.password)
    user_data = {"email": user.email, "password": hashed_password, "roles": user.roles, "permissions": user.permissions,
                 "created_at": datetime.datetime.now(datetime.UTC)}
    user = UserDB.model_validate(user_data)
    id = await users_collection.insert_one(user.model_dump())
    return {"id": str(id.inserted_id)}


@router.get("/users", response_model=UserListResponse)
async def get_users():
    users = await users_collection.find({}, {"__v": 0}).to_list()
    for user in users:
        user["id"] = convert_objectid_to_str(user["_id"])
        del user["_id"]
    return {"status": True, "data": users}


@router.post("/login", response_model=Token)
@limiter.limit("100/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request):
    request_json = await request.json()
    email = request_json['email']
    password = request_json['password']
    user = await authenticate_user(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/logout")
@limiter.limit("1/second")
async def logout(refresh_token: str, request: Request, user=Depends(get_current_user)):
    if user:
        await revoke_token(refresh_token)
        return {"message": "Logged out"}
    else:
        raise HTTPException(status_code=401, detail="Invalid Session")


@router.post("/refresh-token")
@limiter.limit("5/minute")
async def refresh_token_auth(given_refresh_token: str, request: Request):
    try:
        payload = jwt.decode(given_refresh_token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        # Check if the refresh token is revoked
        if await tokens_collection.find_one({"token": given_refresh_token}):
            raise HTTPException(status_code=401, detail="Refresh token revoked")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        new_access_token = create_access_token({"sub": user_id})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/change-password")
async def change_password(user=Depends(get_current_user)):
    hashed_password = hash_password(user.password)
    result = await users_collection.users.update_one({"email": user.email}, {"$set": {"password": hashed_password}})

    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update password")

    return {"status": True, "message": "Password updated successfully"}


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)


async def authenticate_user(email: str, password: str):
    user = await users_collection.find_one({"email": email})
    if user and verify_password(password, user["password"]):
        user = convert_objectid_to_str(user)  # Convert ObjectId to string
        user['id'] = user['_id']
        del user['_id']
        return UserDB(**user)
    return None


async def revoke_token(token: str):
    await tokens_collection.insert_one({"token": token, "revoked_at": datetime.datetime.now(datetime.UTC)})
