# import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse

from ..database.config import user_collection
from ..users_utils import user_exists
from ..collection_utils import collection_exists, get_hashed_files
from ..utils import compute_sha256


# Router to handle the logs
router = APIRouter(
    prefix="/files",
    tags=["files"]
)


# Route to send the log file to the server
# Need a collection name(exist in database) and a user (exist in database and own the collection)
# Need at least one file, can be more
# Can hold a compression type (zip, tar, tar.gz, tar.bz2)
# Return a success message with the status code 201
@router.post("/", status_code=status.HTTP_201_CREATED)
async def post_log_file(files: list[UploadFile], collection: str, username: str):
    # Check if the user exist
    await user_exists(username)
    # Check if the collection exist
    collection_db = await collection_exists(username, collection)
    # Check if at least one file is provided
    if not files.__contains__:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")
    
    list_file_deleted = []
    list_file_write = []
    for file in files:
        file_path = "log/"+file.filename
        # Write the file in the log directory
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        file_hash = await compute_sha256(file_path)

        # check if file have already been parsed
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
