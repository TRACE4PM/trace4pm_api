import hashlib
import os

# import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse

from api.routers.collection import get_collections_names
from api.routers.users import get_user_by_username, get_users
from database.config import database


# Router to handle the logs
router = APIRouter(
    prefix="/files",
    tags=["files"]
)


user_collection = database.get_collection("users")


# Function to get the list of hashed file in a collection
# Return a list of hash
async def get_hashed_files(username: str, collection: str) -> list[str]:
    hashes = await user_collection.find_one(
        {"username": username, "collections.name": collection},
        {"collections.$": 1, "_id": 0})
    return hashes["collections"][0]["files_hash"]


# Function to get the list of files in a directory
# Return a list of files
def get_file_in_dir(dir: str) -> list:
    list_file = []
    for file in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, file)):
            list_file.append(file)
    return list_file


# A utility function that create hash SHA256 of a file
async def compute_sha256(file_name):
    hash_sha256 = hashlib.sha256()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


# Route to send the log file to the server
# Need a collection name(exist in database) and a user (exist in database and own the collection)
# Need at least one file, can be more
# Can hold a compression type (zip, tar, tar.gz, tar.bz2)
# Return a success message with the status code 201
@router.post("/", status_code=status.HTTP_201_CREATED)
async def post_log_file(files: list[UploadFile], collection: str, username: str):
    # Check if the user exist
    if not await user_collection.find_one({"username": username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username doesn't exist")
    # Check if the collection exist
    if collection not in await get_collections_names(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Collection doesn't exist")
    # Check if at least one file is provided
    if not files.__contains__:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")

    coll = database.get_collection(collection)
    list_file_deleted = []
    list_file_write = []
    for file in files:
        file_path = "log/"+file.filename
        # Write the file in the log directory
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        file_hash = await compute_sha256(file_path)
        # check if file have already been parserd

        if file_hash in await get_hashed_files(username, collection):
            list_file_deleted.append(file.filename)

        else:
            await user_collection.update_one(
                {"username": username, "collections.name": collection},
                {"$push": {"collections.$.files_hash": file_hash}})
            list_file_write.append(file.filename)

            # Parse the file
            # await parser(file_path, coll)

        # os.remove("log/"+file.filename)

    # If all files have already been parsed, return an error
    if not list_file_write:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="All files have already been parsed")
    # Else, return a report
    else:
        return {
            "message": "File(s) added to the collection",
            "files added to the collection": list_file_write,
            "files already in the collection": list_file_deleted
        }
