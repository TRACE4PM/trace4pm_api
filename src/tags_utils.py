from fastapi import HTTPException, status
from .collection_utils import purge_collection
from .client_utils import post_clients_in_collection


def trace_handler(trace):
    req = ""
    requests = trace["sessions"]["requests"]
    req_len = len(requests)
    for i, request in enumerate(requests):
        req += request["request_tag"]
        if i < req_len-1:
            req += ","
    return f"{trace['client_id']};{req}"

def trace_handler_action(trace):
    clients_action = list()
    requests = trace["sessions"]["requests"]
    client_id = trace['client_id']
    clients_action = [build_action(client_id, request) for request in requests]
    return clients_action

def build_action(client_id, request):
    action_row = list()
    action_row.append(client_id)
    if "request_tag" in request:
        action_row.append(request["request_tag"])
    else:
        action_row.append(request["request_url"])
    action_row.append(request["request_time"])
    return action_row

async def load_tag_config(collection_db):
    tags_config = [tag async for tag in collection_db.find({},{'_id':0})]
    if not tags_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Tag Config exists yet")
    return tags_config

async def save_tagged_logs(logs_tagged, collection_db) -> None:
    # Remove the old clients from the collection
    await purge_collection(collection_db)
    # Add the client (old and new) to the collection
    await post_clients_in_collection(logs_tagged, collection_db)
