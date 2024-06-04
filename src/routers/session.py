from collections import defaultdict
from datetime import datetime
from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, Request, status, UploadFile
from typing import Annotated, List, Dict, Any
from ..collection_utils import collection_exists
from ..models.users import User_Model
from ..security import get_current_active_user


router = APIRouter(
    prefix="/session/stats",
    tags=["session"]
)



@router.get("/sessions_count", status_code=status.HTTP_200_OK, description="Get the number of sessions for a giving client")
async def get_number_sessions(collection: str, client_id: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]) -> int:
    """This route gets the total number of sessions for a specific client

    Args:
        collection (str): name of the collection containing the clients's logs
        client_id (str): id of a giving client

    Returns:
       The number of sessions of the specified client
    """
    collection_db = await collection_exists(current_user.username, collection)
    client_document = await collection_db.find_one(
        {"client_id": client_id},
        {"_id": 0, "sessions": 1}
    )

    if not client_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    total_sessions = len(client_document.get("sessions", []))

    return total_sessions

@router.get("/requests_count", status_code=status.HTTP_200_OK, description="Get count of requests for a giving client")
async def get_request_count(collection: str, client_id: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]) -> List[Dict[str, Any]]:
    """This route counts the requests of each session for a specific client

    Args:
        collection (str): name of the collection containing the clients's logs
        client_id (str): id of a giving client

    Returns:
        A list of sessions with the number of requests in each session
    """
    collection_db = await collection_exists(current_user.username, collection)
    sessions = [
        request
        async for request in collection_db.find(
            {"client_id": client_id},
            {"_id": 0, "client_id": 1, "country": 1, "sessions": {"requests": 1}},
        )
    ]

    if not sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Request found for this client",
        )

    nb_requests = []
    for session in sessions:
        for i, sess in enumerate(session['sessions']):
            num_requests = len(sess['requests'])
            nb_requests.append({"session": i + 1, "number_requests": num_requests})
            print(f"  Session {i + 1} has {num_requests} requests")

    return nb_requests


@router.get("/clients", status_code=status.HTTP_200_OK, description="Get count of requests for a giving client")
async def get_clients(collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    """This route gets a list of clients' names (user ids)

    Args:
        collection (str): name of the collection containing the clients's logs
    Returns:
        A list of clients' names
    """
    collection_db = await collection_exists(current_user.username, collection)

    try:
        client_ids = await collection_db.distinct("client_id")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving client IDs: {str(e)}"
        )

    if not client_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No client IDs found"
        )

    return client_ids

@router.get("/session_duration", status_code=status.HTTP_200_OK, description="Get count of requests for a giving client")
async def get_session_duration(collection: str,client_id: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    """This route counts the time duration of each session for a specific client

    Args:
        collection (str): name of the collection containing the clients's logs
    Returns:
        A list of sessions with their time duration
    """
    collection_db = await collection_exists(current_user.username, collection)
    sessions = [
        request
        async for request in collection_db.find(
            {"client_id": client_id},
            {"_id": 0, "client_id": 1, "country": 1, "sessions.requests": 1},
        )
    ]

    if not sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No sessions found for this client",
        )

    session_durations = []
    for session in sessions:
        for i, sess in enumerate(session['sessions']):
            request_times = [datetime.fromisoformat(req['request_time']) for req in sess['requests']]
            duration = max(request_times) - min(request_times)
            session_durations.append({"session": i + 1, "duration (seconds)": duration.total_seconds()})

    return session_durations