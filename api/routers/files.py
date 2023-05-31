import hashlib
import json
import os
from parser.main import parser
from parser.models.client import Client_Model
from parser.models.parameters import Parameters

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from typing_extensions import Annotated
from fastapi import Response
from api.models.users import User_Model
from api.routers.collection import (
    get_collection_from_name,
    get_collections_names,
    purge_collection,
)
from api.security import get_current_active_user
from database.client import get_clients_from_collection, post_clients_in_collection
from database.config import database

# Router to handle the logs
router = APIRouter(prefix="/files", tags=["files"])

user_collection = database.get_collection("users")


async def get_hashed_files(username: str, collection: str) -> list[str]:
    """Function to get the list of hashed file in a collection

    Args:
        username (str): username of the user
        collection (str): name of the collection

    Returns:
        list[str]: list of hash
    """
    hashes = await user_collection.find_one(
        {"username": username, "collections.name": collection},
        {"collections.$": 1, "_id": 0},
    )
    return hashes["collections"][0]["files_hash"]


async def get_sha256(file: str):
    """Function to get the SHA256 hash of a file

    Args:
        file (str): path of the file

    Returns:
        str: SHA256 hash of the file
    """
    # Initialize a new SHA-256 hash object
    hash_sha256 = hashlib.sha256()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def post_log_file(
    files: list[UploadFile],
    collection: str,
    current_user: Annotated[User_Model, Depends(get_current_active_user)],
):
    """Route to send logs files to the server and add it to the collection(once parsed)


    Args:
        files (list[UploadFile]): A list of file to parse
        collection (str): name of the collection
        username (str): username of the user

    Returns:
        dict: A report of the files added to the collection
        code: 201
    """
    # Check if the user exist
    if not await user_collection.find_one({"username": current_user.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username doesn't exist"
        )
    # Check if the collection exist
    if collection not in await get_collections_names(current_user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Collection doesn't exist"
        )
    # Check if at least one file is provided
    if not files.__contains__:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided"
        )

    coll = database.get_collection(collection)
    list_file_deleted = []
    list_file_write = []
    tmp = Parameters(
        parser_type="custom",
        parser_format='%h %l %u %t "%r" %>s %b "%{Referer}i" "%{User-Agent}i"',
    )
    for file in files:
        # Write the file in the directory
        file_path: str = "temp/" + file.filename  # type: ignore
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        # check if file have already been parserd
        file_hash = await get_sha256(file_path)
        if file_hash in await get_hashed_files(current_user.username, collection):
            list_file_deleted.append(file.filename)
        else:
            # Parse the file

            list_client = await get_clients_from_collection(coll)

            list_client = await parser(
                file=file_path, collection=list_client, parameters=tmp  # type: ignore
            )

            # Remove the old clients from the collection
            await purge_collection(collection)
            # Add the client (old and new) to the collection
            await post_clients_in_collection(list_client, coll)  # type: ignore
            os.remove(file_path)

            # add the file to the hash list
            await user_collection.update_one(
                {"username": current_user.username, "collections.name": collection},
                {"$push": {"collections.$.files_hash": file_hash}},
            )
            list_file_write.append(file.filename)

    # If all files have already been parsed, return an error
    if not list_file_write:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All files have already been parsed",
        )
    # Else, return a report
    else:
        return {
            "message": "File(s) added to the collection",
            "files added to the collection": list_file_write,
            "files already in the collection": list_file_deleted,
        }


@router.get("/json", status_code=status.HTTP_200_OK)
async def get_json_from_collection(
    collection: str,
    current_user: Annotated[User_Model, Depends(get_current_active_user)],
):
    """Function to get a json object from a collection

    Args:
        collection (str): collection name

    Returns:
        dict: json object
    """
    # Check if the collection exist
    if collection not in await get_collections_names(current_user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Collection doesn't exist"
        )
    collection = await get_collection_from_name(collection)
    json_obj = []
    async for doc in collection.find({}, {"_id": 0}):  # type: ignore
        json_obj.append(json.loads(json.dumps(doc)))
    # if json is empty, return an error
    if not json_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Collection is empty"
        )
    return json_obj
