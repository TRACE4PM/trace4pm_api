from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.encoders import jsonable_encoder

from ..database.config import database
from ..models.users import *
from ..models.collection import *
from datetime import datetime

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

collection = database.get_collection("users")

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
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exist, please choose another username")
    usr = User_Model(**user.dict())
    collection.insert_one(jsonable_encoder(usr))
    return usr


# Route to delete a user
# Return a success message with the status code 200
@router.delete("/{username}", status_code=status.HTTP_200_OK)
async def delete_user(username: str) -> dict:
    if not (await collection.find_one({"username": username})):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username doesn't exist")
    collection.delete_one({"username": username})
    return {"message": "User deleted successfully"}


# Route to get a user by his username
# Return a User_Model object
@router.get("/{username}", status_code=status.HTTP_200_OK)
async def get_user_by_username(username: str) -> User_Model:
    usr = await collection.find_one({"username": username})
    if not usr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username doesn't exist")
    return usr
