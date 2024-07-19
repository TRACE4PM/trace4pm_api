import io
from collections import defaultdict
from datetime import datetime
from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, Request, status, UploadFile
from fastapi.responses import StreamingResponse
from typing import Annotated, List, Dict, Any, Counter
from statistics import mean
import matplotlib.pyplot as plt
from ..collection_utils import collection_exists
from ..models.users import User_Model
from ..security import get_current_active_user
from ..models.response_parameters import ClientSessionDurationResponse, ActionFrequencyResponse

router = APIRouter(
    prefix="/log/stats",
    tags=["LogStats"]
)

@router.get(
    "/traces_duration",
    status_code=status.HTTP_200_OK,

    description="Get the duration of all the traces"
)
async def get_traces_duration(
        collection: str,
        current_user: Annotated[User_Model, Depends(get_current_active_user)]
):
    """This route calculates the time duration of all the traces in the log collection.

    Args:
        collection (str): Name of the collection containing the clients' logs.
        client_id (str): ID of the client whose sessions are to be queried.
        current_user (User_Model): The currently authenticated user.

    Returns:
        List[SessionDurationResponse]: A list of sessions with their time durations.
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

            total_duration_days = total_duration.total_seconds() / (24 * 3600)
            total_duration_weeks = total_duration_days / 7
            client_total_durations.append(
                ClientSessionDurationResponse(
                    client_id=client_id,
                    total_duration_seconds=total_duration.total_seconds(),
                    total_duration_days=total_duration_days,
                    total_duration_weeks=total_duration_weeks
                )
            )

    return client_total_durations

@router.get("/actions_count", status_code=status.HTTP_200_OK,
            description="Counts the occurence of all the actions for a specific client")
async def get_actions_count(collection: str, client_id: str,
                            current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    """This route counts the occurence of all actions for a specific client

    Args:
        collection (str): name of the collection containing the clients's logs
        client_id (str): id of a giving client

    Returns:
        A list of sessions with the number of requests in each session
    """
    try:
        collection_db = await collection_exists(current_user.username, collection)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error accessing collection: {str(e)}"
        )

    try:
        sessions_cursor = collection_db.find({"client_id": client_id}, {"_id": 0, "sessions": 1})
        sessions = await sessions_cursor.to_list(length=None)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sessions: {str(e)}"
        )

    if not sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No sessions found for this client",
        )

    action_frequency = defaultdict(int)
    for session_data in sessions:
        for session in session_data.get('sessions', []):
            for request in session.get('requests', []):
                action = request.get('request_url')
                if action:
                    action_frequency[action] += 1

    total_actions = sum(action_frequency.values())
    if not action_frequency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching requests found for this client",
        )

    return {
        "Total number of actions": total_actions,
        "Actions frequency":  ActionFrequencyResponse(client_id=client_id, action_frequency=dict(action_frequency))
    }


@router.get(
    "/action_frequencies",
    status_code=status.HTTP_200_OK,
    description="Get the frequency of each action in the traces"
)
async def get_actions_frequency_trace(
        collection: str,
        current_user: Annotated[User_Model, Depends(get_current_active_user)]
) -> List[Dict[str, Any]]:
    """This route calculates the frequency of each action in each trace of the log.

    Args:
        collection (str): Name of the collection containing the clients' logs.
        current_user (User_Model): The currently authenticated user.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with case ids and the frequency of each action in the trace.
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
        # Sort the action frequencies by frequency in ascending order
        sorted_actions = dict(sorted(action_counter.items(), key=lambda item: item[1], reverse=True))

        client_action_frequencies.append({
            "client_id": client_id,
            "action_frequency": sorted_actions
        })

    return client_action_frequencies

@router.get(
    "/total_actions_occurrence",
    status_code=status.HTTP_200_OK,
    description="Get the total occurrence of all the actions in the log"
)
async def get_total_actions_occurrence(
        collection: str,
        current_user: Annotated[User_Model, Depends(get_current_active_user)]
) -> Dict[str, Any]:
    """This route calculates the total occurrences of all the actions in the log.

    Args:
        collection (str): Name of the collection containing the clients' logs.
        current_user (User_Model): The currently authenticated user.

    Returns:
        Dict[str, Any]: A dictionary with the total number of actions and their percentages.
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

    total_actions = sum(overall_actions.values())
    sorted_overall_actions = dict(sorted(overall_actions.items(), key=lambda item: item[1], reverse=True))
    return {
        "total_actions": total_actions,
        "action_frequencies": sorted_overall_actions,
    }


@router.get(
    "/total_actions_percentage",
    status_code=status.HTTP_200_OK,
    description="Get the total occurrence of all the actions in the log"
)
async def get_total_actions_percentage(
        collection: str,
        current_user: Annotated[User_Model, Depends(get_current_active_user)]
) -> Dict[str, Any]:
    """This route calculates the percentage of occurence of each action in the log.

    Args:
        collection (str): Name of the collection containing the clients' logs.
        current_user (User_Model): The currently authenticated user.

    Returns:
        Dict[str, Any]: A dictionary with the total number of actions and their percentages.
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

    total_actions = sum(overall_actions.values())
    action_percentages = {action: f"{(count / total_actions) * 100:.2f}%" for action, count in overall_actions.items()}

    sorted_action_percentages = dict(
        sorted(action_percentages.items(), key=lambda item: float(item[1][:-1]), reverse=True))

    return {
        "total_actions": total_actions,
        "action_percentages": sorted_action_percentages
    }


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
        "unique_variant_count": len(trace_variants),
        "unique_variants": trace_variants
    }


@router.get(
    "/distribution_activity_over_time",
    status_code=status.HTTP_200_OK,
    description="This route produces a dotted chart that describes the distribution of the activities over time."
)
async def distribution_activity_over_time(
        collection: str,
        current_user: Annotated[User_Model, Depends(get_current_active_user)]
):
    """This route produces a dotted chart that describes the distribution of the activities over time.

    Args:
        collection (str): Name of the collection containing the clients' logs.
        current_user (User_Model): The currently authenticated user.

    Returns:
        StreamingResponse: The chart image as a streaming response.
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

    request_times = []
    request_urls = []
    for session in sessions:
        for sess in session['sessions']:
            try:
                times_and_urls = [
                    (datetime.fromisoformat(req['request_time']), req['request_url'])
                    for req in sess['requests']
                ]
                request_times.extend([time for time, url in times_and_urls])
                request_urls.extend([url for time, url in times_and_urls])
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error processing session: {str(e)}"
                )

    if not request_times:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No request times found"
        )

    unique_urls = list(set(request_urls))
    url_to_y = {url: idx for idx, url in enumerate(unique_urls)}

    y_values = [url_to_y[url] for url in request_urls]

    # Assign a unique color to each activity
    num_colors = len(unique_urls)
    colors = plt.get_cmap('tab20', num_colors)  # Use 'tab20' colormap
    color_map = {url: colors(idx) for idx, url in enumerate(unique_urls)}
    color_values = [color_map[url] for url in request_urls]

    # Generate the dotted chart
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(request_times, y_values, c=color_values, alpha=0.5)  # Dotted chart with colors
    plt.yticks(range(len(unique_urls)), unique_urls)
    plt.title('Distribution of Activities Over Time')
    plt.xlabel('Time')
    plt.ylabel('Activity')
    plt.grid(True)
    # plt.colorbar(scatter, ticks=range(len(unique_urls)), label='Activities',
    #              format=plt.FuncFormatter(lambda val, loc: unique_urls[loc]))

    # Save the plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")
