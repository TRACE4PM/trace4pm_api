from fastapi import HTTPException, status
from database.config import user_collection

async def user_exists(username: str):
    if not await user_collection.find_one({"username": username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username doesn't exist")