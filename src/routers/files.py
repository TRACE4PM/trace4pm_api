# import aiofiles
import json
import os
from parser.main import parser, csv_parser
from parser.models.csv_parameters import CsvParameters
from parser.models.parameters import Parameters
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from ..collection_utils import collection_exists, get_hashed_files
from ..client_utils import get_clients_from_collection, post_clients_in_collection
from ..database.config import user_collection
from ..models.users import User_Model
from ..security import get_current_active_user
from ..users_utils import user_exists
from ..utils import compute_sha256
from .collection import purge_collection

# Router to handle the logs
router = APIRouter(prefix="/files", tags=["files"])


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

    Returns:
        dict: A report of the files added to the collection
        code: 201
    """
    # Check if the user exist
    await user_exists(current_user.username)
    # Check if the collection exist
    collection_db = await collection_exists(current_user.username, collection)
    # Check if at least one file is provided
    if not files.__contains__:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided"
        )

    list_file_deleted = []
    list_file_write = []
    tmp = Parameters(
        parser_type="custom",
        parser_format='%h %l %u %t "%r" %>s %b "%{Referer}i" "%{User-Agent}i"',
    )
    for file in files:
        file_path = "temp/" + file.filename  # type: ignore
        # Write the file in the log directory
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        file_hash = await compute_sha256(file_path)

        # check if file have already been parsed
        if file_hash in await get_hashed_files(current_user.username, collection):
            list_file_deleted.append(file.filename)
        else:
            # Parse the file

            list_client = await get_clients_from_collection(collection_db)

            list_client = await parser(
                file=file_path, collection=list_client, parameters=tmp  # type: ignore
            )

            # Remove the old clients from the collection
            await purge_collection(collection)
            # Add the client (old and new) to the collection
            await post_clients_in_collection(list_client, collection_db)  # type: ignore
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


# Route for CSV parser (TEST)
@router.post("/csv", status_code=status.HTTP_201_CREATED)
async def post_csv_file(
        files: list[UploadFile],
        collection: str,
        current_user: Annotated[User_Model, Depends(get_current_active_user)],
):
    """Route to send logs files to the server and add it to the collection(once parsed)


    Args:
        files (list[UploadFile]): A list of file to parse
        collection (str): name of the collection

    Returns:
        dict: A report of the files added to the collection
        code: 201
    """
    # Check if the user exist
    print('!!!!!!!!!!! CSV PARSER !!!!!!!!')

    await user_exists(current_user.username)
    # Check if the collection exist
    collection_db = await collection_exists(current_user.username, collection)
    # Check if at least one file is provided
    if not files.__contains__:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided"
        )

    list_file_deleted = []
    list_file_write = []
    # tmp = Parameters(
    #     parser_type="custom",
    #     parser_format='%h %l %u %t "%r" %>s %b "%{Referer}i" "%{User-Agent}i"',
    # )
    tmp = CsvParameters(
        separator=",",
        timestamp_column="timestamp",
        timestamp_format="%d/%m/%y, %H:%M",
        action_column="Description",
        session_id_column="User full name",
        session_time_limit=3600,
    )

    for file in files:
        file_path = "temp/" + file.filename  # type: ignore
        # Write the file in the log directory
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        file_hash = await compute_sha256(file_path)

        # check if file have already been parsed
        if file_hash in await get_hashed_files(current_user.username, collection):
            list_file_deleted.append(file.filename)
        else:
            # Parse the file

            list_client = await get_clients_from_collection(collection_db)

            list_client = await csv_parser(
                file=file_path, collection=list_client, parameters=tmp  # type: ignore
            )

            # Remove the old clients from the collection
            await purge_collection(collection)
            # Add the client (old and new) to the collection
            await post_clients_in_collection(list_client, collection_db)  # type: ignore
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
    collection_db = await collection_exists(current_user.username, collection)
    json_obj = []
    async for doc in collection_db.find({}, {"_id": 0}):  # type: ignore
        json_obj.append(json.loads(json.dumps(doc)))
    # if json is empty, return an error
    if not json_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Collection is empty"
        )
    return json_obj
