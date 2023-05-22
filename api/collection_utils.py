from fastapi import HTTPException, status
from api.routers.collection import get_collections_names
from database.config import database

async def collection_exists(username: str, collection: str):
    if collection not in await get_collections_names(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Collection doesn't exist")
    else:
        return database.get_collection(collection)

