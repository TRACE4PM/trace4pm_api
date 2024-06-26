from collections import defaultdict
from datetime import datetime
from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, Request, status, UploadFile
from typing import Annotated, List, Dict, Any, Counter
from ..collection_utils import collection_exists
from ..models.users import User_Model
from ..security import get_current_active_user
from ..models.cluster_params import ClientSessionDurationResponse


router = APIRouter(
    prefix="/session/stats",
    tags=["session"]
)


@router.get(
    "/trace_variants",
    status_code=status.HTTP_200_OK,
    description="Get the number of unique variants from the traces"
)
async def get_trace_variants(
        collection: str,
        current_user: Annotated[User_Model, Depends(get_current_active_user)]
) -> Dict[str, Any]:
    """This route calculates the number of unique variants from the traces.

    Args:
        collection (str): Name of the collection containing the clients' logs.
        current_user (User_Model): The currently authenticated user.

    Returns:
        Dict[str, Any]: A dictionary with the count of unique variants.
    """
    try:
        collection_db = await collection_exists(current_user.username, collection)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error accessing collection: {str(e)}"
        )

    try:
        sessions = [
            request
            async for request in collection_db.find(
                {},
                {"_id": 0, "sessions.requests": 1}
            )
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sessions: {str(e)}"
        )

    if not sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No sessions found"
        )

    trace_variants = set()

    for session in sessions:
        for sess in session['sessions']:
            try:
                actions = tuple(req['request_url'] for req in sess['requests'])
                trace_variants.add(actions)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error processing session: {str(e)}"
                )

    return {
        "unique_variants": trace_variants,
        "unique_variant_count": len(trace_variants)
    }


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

    return nb_requests


@router.get("/clients", status_code=status.HTTP_200_OK, description="Get a list of clients' names (user ids) ")
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


@router.get(
    "/session_duration",
    status_code=status.HTTP_200_OK,

    description="Get the duration of sessions for a specific client"
)
async def get_session_duration(
    collection: str,
    current_user: Annotated[User_Model, Depends(get_current_active_user)]
) :
    """This route calculates the time duration of each session for a specific client.

    Args:
        collection (str): Name of the collection containing the clients' logs.
        client_id (str): ID of the client whose sessions are to be queried.
        current_user (User_Model): The currently authenticated user.

    Returns:
        List[SessionDurationResponse]: A list of sessions with their time durations.
    """
    try:
        collection_db  = await collection_exists(current_user.username, collection)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error accessing collection: {str(e)}"
        )

    try:
        sessions = [
            request
            async for request in collection_db.find(
                {},
                {"_id": 0, "client_id": 1, "sessions.requests": 1}
            )
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sessions: {str(e)}"
        )

    if not sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No sessions found"
        )

    client_durations = {}
    for session in sessions:
        client_id = session['client_id']
        if client_id not in client_durations:
            client_durations[client_id] = []

        for sess in session['sessions']:
            try:
                request_times = [datetime.fromisoformat(req['request_time']) for req in sess['requests']]
                client_durations[client_id].extend(request_times)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error processing session for client {client_id}: {str(e)}"
                )

    client_total_durations = []
    for client_id, times in client_durations.items():
        if times:
            total_duration = max(times) - min(times)
            client_total_durations.append(
                ClientSessionDurationResponse(client_id=client_id, total_duration_seconds=total_duration.total_seconds()))

    return client_total_durations

@router.get("/actions_count", status_code=status.HTTP_200_OK, description="Get count of an action for a giving client")
async def get_actions_count(collection: str, client_id: str,action: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    """This route counts the occurence of an action for a specific client

    Args:
        collection (str): name of the collection containing the clients's logs
        client_id (str): id of a giving client
        action (str): name of the action to count

    Returns:
        A list of sessions with the number of requests in each session
    """
    collection_db = await collection_exists(current_user.username, collection)
    sessions_cursor = collection_db.find({"client_id": client_id}, {"_id": 0, "sessions": 1})

    sessions = await sessions_cursor.to_list(length=None)

    if not sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Request found for this client",
        )

    total_occurrences = 0
    for session_data in sessions:
        for session in session_data.get('sessions', []):
            total_occurrences += sum(
                1 for request in session.get('requests', []) if request.get('request_url') == action)

    if total_occurrences == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching requests found for this client",
        )

    return total_occurrences


@router.get(
    "/action_frequencies",
    status_code=status.HTTP_200_OK,
    description="Get the frequency of each action for all clients"
)
async def get_action_frequencies(
    collection: str,
    current_user: Annotated[User_Model, Depends(get_current_active_user)]
) -> List[Dict[str, Any]]:
    """This route calculates the frequency of each action for all clients.

    Args:
        collection (str): Name of the collection containing the clients' logs.
        current_user (User_Model): The currently authenticated user.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with client IDs and their action frequencies.
    """
    try:
        collection_db= await collection_exists(current_user.username, collection)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error accessing collection: {str(e)}"
        )

    try:
        sessions = [
            request
            async for request in collection_db.find(
                {},
                {"_id": 0, "client_id": 1, "sessions.requests": 1}
            )
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sessions: {str(e)}"
        )

    if not sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No sessions found"
        )

    client_actions = {}
    for session in sessions:
        client_id = session['client_id']
        if client_id not in client_actions:
            client_actions[client_id] = Counter()

        for sess in session['sessions']:
            try:
                actions = [req['request_url'] for req in sess['requests']]
                client_actions[client_id].update(actions)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error processing session for client {client_id}: {str(e)}"
                )

    client_action_frequencies = []
    for client_id, action_counter in client_actions.items():
        client_action_frequencies.append({
            "client_id": client_id,
            "action_frequencies": dict(action_counter)
        })

    return client_action_frequencies

@router.get(
    "/actions_counter",
    status_code=status.HTTP_200_OK,
    description="Get the frequency of each action for all clients"
)
async def get_actions_freq_traces(
        collection: str,
        current_user: Annotated[User_Model, Depends(get_current_active_user)]
) -> Dict[str, Any]:
    """This route calculates the frequency of each action overall traces.

    Args:
        collection (str): Name of the collection containing the clients' logs.
        current_user (User_Model): The currently authenticated user.

    Returns:
        Dict[str, Any]: A dictionary with client IDs and their action frequencies, and overall action frequencies.
    """
    try:
        collection_db= await collection_exists(current_user.username, collection)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error accessing collection: {str(e)}"
        )

    try:
        sessions = [
            request
            async for request in collection_db.find(
                {},
                {"_id": 0, "client_id": 1, "sessions.requests": 1}
            )
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sessions: {str(e)}"
        )

    if not sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No sessions found"
        )

    client_actions = {}
    overall_actions = Counter()

    for session in sessions:
        client_id = session['client_id']
        if client_id not in client_actions:
            client_actions[client_id] = Counter()

        for sess in session['sessions']:
            try:
                actions = [req['request_url'] for req in sess['requests']]
                client_actions[client_id].update(actions)
                overall_actions.update(actions)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error processing session for client {client_id}: {str(e)}"
                )


    return dict(overall_actions)