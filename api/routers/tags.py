from fastapi import APIRouter, HTTPException, status, Depends, UploadFile
from typing import Annotated
import os
from ..models.users import User_Model
from ..security import get_current_active_user
from ..collection_utils import collection_exists
from ..tags_utils import load_tag_config, save_tagged_logs
from tagging.main import generate
from tagging.utils import validate_json_content

router = APIRouter(
    prefix="/tags",
    tags=["tags"]
)

# Apply tagging for each request_url and save them to db
@router.get("/generate", status_code=status.HTTP_200_OK)
async def generate_tags(tag_collection: str, log_collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    log_db = await collection_exists(current_user.username, log_collection)
    tag_db = await collection_exists(current_user.username, tag_collection)
    clients = [client async for client in log_db.find({},{'_id':0})]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client's log exists yet")
    tags_config = await load_tag_config(tag_db)
    logs_tagged = await generate(tags_config, clients)
    if not logs_tagged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_ERROR, detail="Error while generating the tags")
    await save_tagged_logs(logs_tagged, log_db)

    return {"message": "Tags successfully generated"}


# Upload the rules from a json file
@router.post("/upload_rules", status_code=status.HTTP_200_OK)
async def upload_and_save_rules(collection: str, file: UploadFile, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    
    try:
        file_ext = os.path.splitext(file.filename)[1]
        # Check if a json file has been uploaded
        if not file or file_ext.lower() != ".json":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="You should upload a json file"
            )
    except:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Error while uploading the json file"
            )

    try:
        file_contents = await file.read()
        parsed_file = await validate_json_content(file_contents)
        await collection_db.insert_many(parsed_file)
    except:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Error while processing the json file"
            )

    return {"message": "Json file successfully uploaded"}
    


# Return the rules
@router.get("/get_rules", status_code=status.HTTP_200_OK)
async def get_tagging_rules(collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    tags = [tag async for tag in collection_db.find({},{'_id':0})]
    if not tags:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No rule exists yet")
    return tags