from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends
from typing import Annotated
from api.security import get_current_active_user, get_password_hash

from api.models.collection import *
from api.models.users import *
from database.config import database

router = APIRouter(prefix="/users", tags=["users"])

collection = database.get_collection("users")


@router.get("/me/", response_model=User_Model)
async def read_users_me(
    current_user: Annotated[User_Model, Depends(get_current_active_user)]
):
    return current_user


# Route to get the list of users
# Return a list of User_Model objects
@router.get("/")
async def get_users() -> list[User_Model]:
    list_users = []
    async for usr in collection.find({}, {"_id": 0}):
        list_users.append(usr)
    return list_users


# Route to create a user
# Return a success message with the status code 201
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: User_Create_Model) -> User_Model:
    user.username = user.username.lower()
    if await collection.find_one({"username": user.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exist, please choose another username",
        )
    hash_pwd = get_password_hash(user.plain_password)
    usr = User_inDB_Model(
        username=user.username,
        firstname=user.firstname,
        hashed_password=hash_pwd,
    )
    collection.insert_one(jsonable_encoder(usr))
    return usr


# Route to delete a user
# Return a success message with the status code 200
@router.delete("/{username}", status_code=status.HTTP_200_OK)
async def delete_user(username: str) -> dict:
    if not (await collection.find_one({"username": username})):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username doesn't exist"
        )
    collection.delete_one({"username": username})
    return {"message": "User deleted successfully"}
