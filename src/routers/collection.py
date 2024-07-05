from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends

from ..collection_utils import get_log_collections, get_cluster_collections, get_collections_names, remove_null_values
from ..database.config import database, user_collection
from ..models.collection import *
from ..models.users import User_Model
from ..security import get_current_active_user
from ..users_utils import user_exists

router = APIRouter(prefix="/collection", tags=["collection"])


# Route to create a collection for a user
# Create a collection in database
# Return the collection created with the status code 201
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_collection(
        collection: Collection_Create_Model,
        current_user: Annotated[User_Model, Depends(get_current_active_user)],
):
    collection.name = collection.name
    # check if user exists
    await user_exists(current_user.username)
    # Check if collection name already exists
    if collection.name in await get_collections_names(current_user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Collection already exists, please choose another name",
        )

    # Ensure coll is always defined
    if collection.log_collection:
        coll = Collection_Model(
            **collection.dict(),
            created_at=datetime.strftime(datetime.now(), "%d/%m/%Y %H:%M:%S"),
            file_name=None,
            files_hash=[]
        )
    else:
        coll = Clustering_Collection_Model(
            **collection.dict(),
            created_at=datetime.strftime(datetime.now(), "%d/%m/%Y %H:%M:%S"),
            file_name=None,
            files_hash=[],
            clustering_approach=None,
            clustering_parameters=[],
            clustering_result=[]
        )

    # Add collection to user collections
    await user_collection.update_one(
        {"username": current_user.username},
        {"$push": {"collections": jsonable_encoder(coll)}},
    )
    # Create collection in database
    await database.create_collection(coll.name)
    return coll


# Route to get the list of log collections in database
# Return a list of collections with the status code 200
@router.get("/list_log_collections", status_code=status.HTTP_200_OK)
async def list_log_collections(
        current_user: Annotated[User_Model, Depends(get_current_active_user)]
) -> list[Collection_Model]:
    collections = await get_log_collections(current_user.username)
    return collections


# Route to return a list of cluster collections in the database
@router.get("/list_cluster_collections", status_code=status.HTTP_200_OK)
async def list_cluster_collections(
        current_user: Annotated[User_Model, Depends(get_current_active_user)]
) -> list[Clustering_Collection_Model]:
    collections = await get_cluster_collections(current_user.username)
    return collections


# Route to delete a collection in database
# Return a success message with the status code 200
@router.delete("/", status_code=status.HTTP_200_OK)
async def delete_collection(
        current_user: Annotated[User_Model, Depends(get_current_active_user)],
        collection: str,
) -> dict:
    # check if user exist
    await user_exists(current_user.username)
    if collection not in await get_collections_names(current_user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Collection doesn't exist"
        )
    # Delete collection from user collections
    await user_collection.update_one(
        {"username": current_user.username},
        {"$pull": {"collections": {"name": collection}}},
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
