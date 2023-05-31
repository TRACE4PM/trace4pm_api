from fastapi import HTTPException, status
from .database.config import database, user_collection
from .models.collection import Collection_Model

async def collection_exists(username: str, collection: str):
    if collection not in await get_collections_names(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Collection doesn't exist")
    else:
        return database.get_collection(collection)

# Function to get the list of collections names in database
# Return a list of collections names
async def get_collections_names(username: str) -> list[str]:
    list_names = []
    async for names in user_collection.find({"username": username}, {"_id": 0, "collections.name": 1}):
        for name in names["collections"]:
            list_names.append(name["name"])
    return list_names


# Function to list the collections of a user
# Return a list of collections
async def get_all_collections(username: str) -> list[Collection_Model]:
    document = await user_collection.find_one({"username": username}, {"_id": 0})
    if not document:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username doesn't exist")
    collections = document["collections"]
    return collections


# Function to get a collection-object by name
# Return a collection-object
async def get_collection_from_name(collection_name: str):
    # Check if collection exist
    if collection_name not in await database.list_collection_names():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Collection doesn't exist")
    return database.get_collection(collection_name)


# Function to get the list of hashed file in a collection
# Return a list of hash
async def get_hashed_files(username: str, collection: str) -> list[str]:
    hashes = await user_collection.find_one(
        {"username": username, "collections.name": collection},
        {"collections.$": 1, "_id": 0})
    return hashes["collections"][0]["files_hash"]

