from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from api.models.client import Client_Get_Model
from database.config import collection_users_logs as users_logs
from api.tags_utils import get_tagged_logs, update_logs

router = APIRouter(
    prefix="/tags",
    tags=["tags"]
)


# Apply tagging for each request_url and return a json for the request_url tagged
@router.get("/generate", status_code=status.HTTP_200_OK)
async def generating_tags():
    clients = [client async for client in users_logs.find({}, {'client_id': 1, "sessions.requests.request_url": 1, '_id': 0})]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client's log exists yet")
    tagged_logs = get_tagged_logs(clients)
    return tagged_logs


# Apply tagging for each request_url and save them to db
@router.get("/load_save", status_code=status.HTTP_200_OK)
async def load_tag_save():
    clients = [client async for client in users_logs.find()]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client's log exists yet")
    logs_tagged = update_logs(clients)
    if logs_tagged:
        return {"message": "Tags successfully generated"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_ERROR, detail="Error while generating the tags")
