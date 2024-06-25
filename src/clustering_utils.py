import os
import csv
import io
import tempfile
import zipfile
import pandas as pd
from datetime import datetime
from typing import List, Annotated, Dict, Any
from fastapi import HTTPException, UploadFile, status, File, Depends
from parser.main import csv_parser
from parser.models.csv_parameters import CsvParameters
from parser.models.session import Session_Model
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

    if collection_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )

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
        timestamp_format="%Y-%m-%d %H:%M:%S",
        action_column="action",
        session_id_column="client_id",
        session_time_limit=3600,
        cluster_id="cluster_id"
    )

    for file in files:

        filename = os.path.basename(file)
        file_hash = await compute_sha256(file)

        # check if file have already been parsed
        if file_hash in await get_hashed_files(current_user.username, collection):
            list_file_deleted.append(filename)
        else:
            # Parse the file
            list_client = await get_clients_from_collection(collection_db)
            list_client = csv_parser(
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


def empty_directory(directory_path):
    # Remove the files already existing a directory
    if os.path.exists(directory_path):
        files = os.listdir(directory_path)
        for file in files:
            os.remove(os.path.join(directory_path, file))


def convert_to_csv(file_content, delimiter=','):
    output = StringIO()
    writer = csv.writer(output, delimiter=delimiter)
    writer.writerows(file_content)
    return output.getvalue()


async def fetch_documents(collection_db: Any) -> List[Dict]:
    """Fetch documents from the collection."""
    documents = []
    async for doc in collection_db.find({}, {"_id": 0}):
        documents.append(doc)
    if not documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Collection is empty"
        )
    return documents


async def fetch_documents(collection_db: Any) -> List[Dict]:
    """Fetch documents from the collection."""
    documents = []
    async for doc in collection_db.find({}, {"_id": 0}):
        documents.append(doc)
    if not documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Collection is empty"
        )
    return documents

def create_csv_files(documents: List[Dict], directory: str) -> List[str]:
    """Create CSV files from the json files in the collection"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory {directory} created.")
    else:
        empty_directory(directory)

    writers = {}
    file_paths = []

    for doc in documents:
        client_id = doc.get("client_id", "unknown")
        sessions = doc.get("sessions", [])
        for session in sessions:
            requests = session.get("requests", [])
            for request in requests:
                cluster_id = request.get("cluster_id")
                if cluster_id is None:
                    continue

                file_path = os.path.join(directory, f"cluster_{cluster_id}.csv")
                file_exists = os.path.isfile(file_path)

                if cluster_id not in writers:
                    file = open(file_path, "a", newline='')
                    writer = csv.writer(file, delimiter=";")
                    writers[cluster_id] = (writer, file)

                    if not file_exists:
                        writer.writerow(["client_id", "action", "timestamp"])

                writer, _ = writers[cluster_id]
                writer.writerow([
                    client_id,
                    request.get("request_url"),
                    request.get("request_time")
                ])

    for writer, file in writers.values():
        file.close()
        file_paths.append(file.name)
        print(f"File closed: {file.name}")

    return file_paths

def create_zip_file(file_paths: List[str]) -> str :
    """Create a zip file containing the CSV files."""
    temp_dir = tempfile.mkdtemp()
    zip_file_path = os.path.join(temp_dir, "clusters.zip")

    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in file_paths:
            zip_file.write(file_path, os.path.basename(file_path))
    return zip_file_path