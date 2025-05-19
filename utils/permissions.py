from bson import ObjectId
from fastapi import Depends, HTTPException

from utils.database import roles_collection
from models.role import RoleDB
from utils.helper import convert_objectid_to_str
from utils.helper import get_current_user


async def get_role_permissions(roles: str):
    db_roles = []
    for role in roles:
        role_find = await roles_collection.find_one({"name": role})
        role_find = convert_objectid_to_str(role_find)
        db_roles += RoleDB(**role_find).permissions
    return db_roles


def check_permission(required_permission: str):
    async def permission_checker(user: dict = Depends(get_current_user)):
        role_permissions = await get_role_permissions(user.roles)
        if '*' in role_permissions:
            return user
        if required_permission not in role_permissions and required_permission not in user.permissions:
            raise HTTPException(status_code=403, detail="Permission denied")
        return user

    return permission_checker
