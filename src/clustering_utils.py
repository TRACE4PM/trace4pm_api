import os
from typing import List, Annotated
from fastapi import HTTPException, UploadFile, status, File, Depends
from parser.main import csv_parser
from parser.models.csv_parameters import CsvParameters
from .client_utils import get_clients_from_collection, post_clients_in_collection
from .collection_utils import collection_exists, get_hashed_files, purge_collection
from .database.config import user_collection
from .models.users import User_Model
from .security import get_current_active_user
from .users_utils import user_exists
from .utils import compute_sha256


async def post_clusters(
        files,
        collection,
        current_user: Annotated[User_Model, Depends(get_current_active_user)],
):

    # Check if the user exist
    print('!!!!!!!!!!! CSV PARSER !!!!!!!!')

    await user_exists(current_user.username)
    # Check if the collection exist
    collection_db = await collection_exists(current_user.username, collection)
    print("col db", collection_db)
    # Check if at least one file is provided
    if not files.__contains__:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided"
        )

    list_file_deleted = []
    list_file_write = []

    tmp = CsvParameters(
        separator=";",
        timestamp_column="timestamp",
        timestamp_format="%Y-%m-%d %H:%M:%S%z",
        action_column="action",
        session_id_column="client_id",
        session_time_limit=3600,
    )

    for file in files:
        print(file)
        filename = os.path.basename(file)
        file_hash = await compute_sha256(file)

        # check if file have already been parsed
        if file_hash in await get_hashed_files(current_user.username, collection):
            list_file_deleted.append(filename)
        else:
            # Parse the file
            list_client = await get_clients_from_collection(collection_db)
            list_client = await csv_parser(
                file=file, collection=list_client, parameters=tmp  # type: ignore
            )

            # Add the clients to the collection
            await post_clients_in_collection(list_client, collection_db)  # type: ignore
            os.remove(file)
            # add the file to the hash list
            await user_collection.update_one(
                {"username": current_user.username, "collections.name": collection},
                {"$push": {"collections.$.files_hash": file_hash}},
            )
            list_file_write.append(filename)
    # If all files have already been parsed, return an error
    if not list_file_write:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All files have already been parsed",
        )

    else:
        return {
            "message": "File(s) added to the collection",
            "files added to the collection": list_file_write,
            "files already in the collection": list_file_deleted,
        }
