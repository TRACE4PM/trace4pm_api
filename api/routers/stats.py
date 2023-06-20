from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import FileResponse
from typing import Annotated
from ..models.users import User_Model
from ..security import get_current_active_user
from parser.models.client import Client_Get_Model
from ..stats_utils import *
from ..tags_utils import trace_handler
from ..users_utils import user_exists
from ..collection_utils import collection_exists
from heapq import nlargest
from heapq import nsmallest

router = APIRouter(prefix="/stats", tags=["stats"])


# Get the number of clients for a specific country grouped by city
@router.get("/country/group_city/", status_code=status.HTTP_200_OK, description="Get the number of clients grouped by city for a specific country")
async def get_number_of_clients_grouped_by_city(
    collection: str, country_name: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    clients = [
        client
        async for client in collection_db.aggregate(
            [
                {"$match": {"country": {'$regex': country_name, "$options": "i" }}},
                {"$group": {"_id": "$city", "Total": {"$count": {}}}},
                {"$sort": {"_id": 1}},
                {'$project':{'_id': 0,'City': '$_id', 'Total': 1}}
            ]
        )
    ]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Client exists yet for this country",
        )
    return clients


# Get the number of clients for a specific city
@router.get("/city/", status_code=status.HTTP_200_OK, description="Get the number of clients grouped by city for a specific country")
async def get_number_of_clients_for_a_city(
    collection: str, city_name: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    clients = [
        client
        async for client in collection_db.aggregate(
            [{"$match": {"city": {'$regex': city_name, "$options": "i" }}}, {"$count": "Total"}]
        )
    ]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Client exists yet for this city",
        )
    return clients[0]


# Get the number of request for a tag
@router.get("/requests/", status_code=status.HTTP_200_OK)
async def get_number_of_request_for_a_tag(
    collection: str, tag_name: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    stat = [
        stat
        async for stat in collection_db.aggregate(
            [
                {"$unwind": "$sessions"},
                {"$unwind": "$sessions.requests"},
                {"$match": {"sessions.requests.request_tag": {'$regex': tag_name, "$options": "i" }}},
                {
                    "$group": {
                        "_id": "$sessions.requests.request_tag",
                        "Quantity": {"$count": {}},
                    }
                },
                {"$project": {"_id": 0, "Request Type": "$_id", "Quantity": 1}}
            ]
        )
    ]
    if not stat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No statistics found for this tag",
        )
    return stat


# Get the number of requests grouped by tag
@router.get("/requests/group_tag/", status_code=status.HTTP_200_OK)
async def get_requests_grouped_by_tag(collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    stat = [
        stat
        async for stat in collection_db.aggregate(
            [
                {"$unwind": "$sessions"},
                {"$unwind": "$sessions.requests"},
                {
                    "$group": {
                        "_id": "$sessions.requests.request_tag",
                        "Quantity": {"$count": {}},
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "data": {"$push": {"k": "$_id", "v": "$Quantity"}}
                    }
                },
                {
                    "$replaceRoot": {
                        "newRoot": {"$arrayToObject": "$data"}
                    }
                }
            ]
        )
    ]
    if not stat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No data found"
        )
    return stat[0]


# Count the number of requests that appear a specific amount of time
@router.get("/requests/request_count/", status_code=status.HTTP_200_OK)
async def get_number_of_request(collection: str, quantity: int, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    stat = [
        stat
        async for stat in collection_db.aggregate(
            [
                {"$unwind": "$sessions"},
                {"$unwind": "$sessions.requests"},
                {"$match": {"sessions.requests.request_tag": {"$ne": "Outliers"}}},
                {
                    "$group": {
                        "_id": "$sessions.requests.request_url",
                        "Qte": {"$count": {}},
                    }
                },
                {"$match": {"Qte": {"$eq": quantity}}},
                {"$count": "Total"},
            ]
        )
    ]
    if not stat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No data found"
        )
    return stat


# Get a specific client's traces
@router.get("/client_trace/", status_code=status.HTTP_200_OK)
async def get_client_trace(collection: str, client_id: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    traces = [
        trace_handler(trace)
        async for trace in collection_db.aggregate(
            [
                {"$match": {"client_id": client_id}},
                {"$unwind": "$sessions"},
                {
                    "$project": {
                        "_id": 0,
                        "client_id": 1,
                        "sessions.requests": {
                            "$filter": {
                                "input": "$sessions.requests",
                                "as": "request",
                                "cond": {"$ne": ["$$request.request_tag", "Outliers"]},
                            }
                        },
                    }
                },
                {"$match": {"sessions.requests": {"$ne": []}}},
            ]
        )
    ]
    if not traces:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No data found for this client",
        )
    return traces


# Get all clients's traces
@router.get("/clients_traces/", status_code=status.HTTP_200_OK)
async def get_clients_traces(collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    return await get_traces(collection_db)


# Get unique trace number
@router.get("/unique_trace/", status_code=status.HTTP_200_OK)
async def get_unique_trace_number(collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    trace_list = await get_traces(collection_db)
    unique_trace = list()
    for trace in trace_list:
        trace_tags = trace.split(";")[1]
        if not unique_trace.__contains__(trace_tags):
            unique_trace.append(trace_tags)
    return {"Trace number": len(trace_list), "Unique Trace Number": len(unique_trace)}


# Get popularity trace
@router.get("/popularity_trace/", status_code=status.HTTP_200_OK)
async def get_popularity_trace(collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    trace_list = await get_traces(collection_db)
    return await get_popularity(trace_list)


# Get most popular trace
@router.get("/most_popular_trace/", status_code=status.HTTP_200_OK)
async def get_most_popular_trace(
    collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)], number: int | None = 5):
    collection_db = await collection_exists(current_user.username, collection)
    trace_list = await get_traces(collection_db)
    popularity = await get_popularity(trace_list)
    return nlargest(number, popularity, key=popularity.get)


# Get less popular trace
@router.get("/less_popular_trace/", status_code=status.HTTP_200_OK)
async def get_less_popular_trace(
    collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)], number: int | None = 5
):
    collection_db = await collection_exists(current_user.username, collection)
    trace_list = await get_traces(collection_db)
    popularity = await get_popularity(trace_list)
    return nsmallest(number, popularity, key=popularity.get)


# Get average action
@router.get("/average_trace/", status_code=status.HTTP_200_OK)
async def get_average_trace(collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    trace_len, unique_trace = await unique_trace_number(collection_db)
    return {"Average ": trace_len / unique_trace}


# Get stat trace string
@router.get("/stat_trace_string/", status_code=status.HTTP_200_OK)
async def get_stat_trace_string(collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    trace_len, unique_trace = await unique_trace_number(collection_db)
    average = trace_len / unique_trace
    return {
        "Total": trace_len.__str__(),
        "Unique": unique_trace.__str__(),
        "Average": average.__str__(),
    }

# Get all clients's actions
#@router.get("/clients_actions/", status_code=status.HTTP_200_OK, description="Return all clients's actions in a csv file")
@router.get("/clients_actions/", status_code=status.HTTP_200_OK, response_class=FileResponse, description="Return all clients's actions in a csv file")
async def get_clients_actions(collection: str, filename: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    clients_action = await get_clients_action(collection_db)
    csv_file = await create_csv_file(clients_action,filename)
    response = FileResponse(csv_file, media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}.csv"
    return response


# Get unique action number
@router.get("/unique_action/", status_code=status.HTTP_200_OK, description="Return the number of unique action")
async def get_unique_action_number(collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    act_number, unique_action = await unique_action_infos(collection_db)
    return {"Action number": act_number, "Unique action Number": len(unique_action)}


# Get popularity action
@router.get("/popularity_action/", status_code=status.HTTP_200_OK, description="Return the popularity of each single action")
async def get_popularity_action(collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    action_list = await get_actions(collection_db)
    return await popularity_action(action_list)


# Get most popular action
@router.get("/most_popular_action/", status_code=status.HTTP_200_OK, description="Return the x most popular action (the default of x is 5)")
async def get_most_popular_action(
    collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)], number: int | None = 5):
    collection_db = await collection_exists(current_user.username, collection)
    action_list = await get_actions(collection_db)
    popularity = await popularity_action(action_list)
    return nlargest(number, popularity, key=popularity.get)


# Get less popular action
@router.get("/less_popular_action/", status_code=status.HTTP_200_OK, description="Return the x less popular action (the default of x is 5)")
async def get_less_popular_action(
    collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)], number: int | None = 5
):
    collection_db = await collection_exists(current_user.username, collection)
    action_list = await get_actions(collection_db)
    popularity = await popularity_action(action_list)
    return nsmallest(number, popularity, key=popularity.get)

# Get average action
@router.get("/average_action/", status_code=status.HTTP_200_OK, description="Return the average of the action based on the number of action and the unique action number")
async def get_average_action(collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    act_number, unique_action = await unique_action_infos(collection_db)
    return {"Average ": act_number / len(unique_action)}

# Get action's number
@router.get("/action_number/", status_code=status.HTTP_200_OK)
async def get_action_number(collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    act_number = await action_number(collection_db)
    if act_number <= 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No action found")
    return {"Action Number": act_number}

# Get stat action string
@router.get("/stat_action_string/", status_code=status.HTTP_200_OK)
async def get_stat_action_string(collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    act_number, unique_action = await unique_action_infos(collection_db)
    average = act_number / len(unique_action)
    return {
        "Total": act_number.__str__(),
        "Unique": len(unique_action).__str__(),
        "Average": average.__str__(),
    }
