from fastapi import APIRouter, HTTPException, status
from ..users_utils import user_exists
from ..collection_utils import collection_exists
from ..tags_utils import load_tag_config, save_tagged_logs
from ..database.config import tag_config
from tagging.main import generate

router = APIRouter(
    prefix="/tags",
    tags=["tags"]
)

# Apply tagging for each request_url and save them to db
@router.get("/generate", status_code=status.HTTP_200_OK)
async def generate_tags(username: str, collection: str):
    await user_exists(username)
    collection_db = await collection_exists(username, collection)
    clients = [client async for client in collection_db.find({},{'_id':0})]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client's log exists yet")
    tags_config = await load_tag_config(tag_config)
    logs_tagged = await generate(tags_config, clients)
    if not logs_tagged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_ERROR, detail="Error while generating the tags")
    await save_tagged_logs(logs_tagged, collection_db)

    return {"message": "Tags successfully generated"}