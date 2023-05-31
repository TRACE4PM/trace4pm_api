import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder

from ..models.collection import *
from ..database.config import user_collection, database
from ..users_utils import user_exists
from ..collection_utils import get_collections_names, get_all_collections, get_collection_from_name

router = APIRouter(
    prefix="/collection",
    tags=["collection"]
)


# Route to create a collection for a user
# Create a collection in database
# Return the collection created with the status code 201
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_collection(username: str, collection: Collection_Create_Model) -> Collection_Model:
    collection.name = collection.name.lower()
    # check if user exist
    await user_exists(username)
    # Check if collection name already exist
    if collection.name in await get_collections_names(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Collection already exist, please choose another name")

    coll = Collection_Model(**collection.dict(),
                            created_at=datetime.strftime(
                                datetime.now(), "%d/%m/%Y %H:%M:%S"),
                            files_hash=[])
    # Add collection to user collections
    await user_collection.update_one(
        {"username": username},
        {"$push": {"collections": jsonable_encoder(coll)}}
    )
    # Create collection in database
    await database.create_collection(coll.name)
    return coll


# Route to get the list of collections in database
# Return a list of collections with the status code 200
@router.get("/", status_code=status.HTTP_200_OK)
async def list_collections(username: str) -> list[Collection_Model]:
    collections = await get_all_collections(username)
    return collections


# Route to delete a collection in database
# Return a success message with the status code 200
@router.delete("/", status_code=status.HTTP_200_OK)
async def delete_collection(username: str, collection: str) -> dict:
    # check if user exist
    await user_exists(username)
    collection = collection.lower()
    if collection not in await get_collections_names(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Collection doesn't exist")
    # Delete collection from user collections
    await user_collection.update_one(
        {"username": username},
        {"$pull": {"collections": {"name": collection}}}
    )
    # Delete collection for database
    database.drop_collection(collection)
    return {"Success": "Collection deleted successfully"}


# Route to purge a collection in database
# Take a collection name as parameter
# Doesn't delete the files hash
# Return a success message with the status code 200
@router.delete("/purge/", status_code=status.HTTP_200_OK)
async def purge_collection(collection: str) -> dict:
    # Delete all documents in collection
    await database[collection].delete_many({})
    return {"Success": "Collection purged successfully"}


# Function to make json files from collection
# Return a json object
@router.get("/json", status_code=status.HTTP_200_OK)
async def get_json_from_collection(collection: str):
    collection_db = await get_collection_from_name(collection)
    json_obj = []
    async for doc in collection_db.find({}, {"_id": 0}):
        json_obj.append(json.loads(json.dumps(doc)))
    return json_obj
