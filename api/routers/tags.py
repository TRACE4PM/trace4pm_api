from fastapi import APIRouter, HTTPException, status
from api.tags_utils import update_logs
from api.users_utils import user_exists
from api.collection_utils import collection_exists

router = APIRouter(
    prefix="/tags",
    tags=["tags"]
)

# Apply tagging for each request_url and save them to db
@router.get("/generate", status_code=status.HTTP_200_OK)
async def load_tag_save(username: str, collection: str):
    await user_exists(username)
    collection_db = await collection_exists(username, collection)
    clients = [client async for client in collection_db.find()]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client's log exists yet")
    logs_tagged = update_logs(clients, collection_db)
    if logs_tagged:
        return {"message": "Tags successfully generated"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_ERROR, detail="Error while generating the tags")
