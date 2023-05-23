from fastapi import APIRouter, HTTPException, status
from api.models.client import Client_Get_Model
from api.tags_utils import trace_handler
from api.users_utils import user_exists
from api.collection_utils import collection_exists
from heapq import nlargest
from heapq import nsmallest

router = APIRouter(
    prefix="/stats",
    tags=["stats"]
)

# Get the number of clients for a specific country grouped by city
@router.get("/country/", status_code=status.HTTP_200_OK)
async def get_number_of_clients_grouped_by_city(username: str, collection: str, country_name: str):
    await user_exists(username)
    collection_db = await collection_exists(username, collection)
    clients = [client async for client in collection_db.aggregate([{'$match': {'country': country_name}}, {'$group': {'_id': "$city", 'Total': { '$count': {}}}}, { '$sort': {'_id': 1}}])]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client exists yet for this country")
    return clients

# Get the number of clients for a specific city
@router.get("/city/", status_code=status.HTTP_200_OK)
async def get_number_of_clients_for_a_city(username: str, collection: str, city_name: str):
    await user_exists(username)
    collection_db = await collection_exists(username, collection)
    clients = [client async for client in collection_db.aggregate([{'$match': {'city': city_name}}, {'$count': 'Total'}])]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client exists yet for this city")
    return clients[0]

# Get the number of request for a tag
@router.get("/requests/", status_code=status.HTTP_200_OK)
async def get_number_of_request_for_a_tag(username: str, collection: str, tag_name: str):
    await user_exists(username)
    collection_db = await collection_exists(username, collection)
    stat = [stat async for stat in collection_db.aggregate([
        {'$unwind': "$sessions" },{'$unwind': "$sessions.requests" },{'$match': {"sessions.requests.request_tag": tag_name}}, 
        {'$group': {'_id': "$sessions.requests.request_tag", 'Quantity': { '$count': {}}}},{ "$project": {"_id":0, "Request Type": "$_id", "Quantity": 1}}])]
    if not stat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No statistics found for this tag")
    return stat


# Get the number of requests grouped by tag
@router.get("/requests/group_tag/", status_code=status.HTTP_200_OK)
async def get_requests_grouped_by_tag(username: str, collection: str):
    await user_exists(username)
    collection_db = await collection_exists(username, collection)
    stat = [stat async for stat in collection_db.aggregate([
        {'$unwind': "$sessions" },{'$unwind': "$sessions.requests" }, 
        {'$group': {'_id': "$sessions.requests.request_tag", 'Quantity': { '$count': {}}}},{ "$project": {"_id":0, "Request Type": "$_id", "Quantity": 1}}])]
    if not stat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No data found")
    return stat

# Count the number of requests that appear a specific amount of time
@router.get("/requests/request_count/", status_code=status.HTTP_200_OK)
async def get_number_of_request(username: str, collection: str, quantity:int):
    await user_exists(username)
    collection_db = await collection_exists(username, collection)
    stat = [stat async for stat in collection_db.aggregate([
        { '$unwind': "$sessions" },{ '$unwind': "$sessions.requests" },
        {'$match': {"sessions.requests.request_tag": {'$ne':"Outliers"}}},
        {'$group': {'_id': "$sessions.requests.request_url", 'Qte': { '$count': {}}}},
        {'$match': {'Qte': {'$eq':quantity}}},
        {'$count': 'Total'}])]
    if not stat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No data found")
    return stat

# Get a specific client's traces
@router.get("/client_trace/", status_code=status.HTTP_200_OK)
async def get_client_trace(username: str, collection: str, client_id: str):
    await user_exists(username)
    collection_db = await collection_exists(username, collection)
    traces = [trace_handler(trace) async for trace in collection_db.aggregate([
        {"$match": {"client_id":client_id}},
        {"$unwind": "$sessions" },
        {
            "$project": {
                "_id":0, 
                "client_id":1, 
                "sessions.requests": {
                    "$filter": {
                        "input": "$sessions.requests",
                        "as": "request",
                        "cond": {"$ne": ["$$request.request_tag", "Outliers"] }
                    }
                }
            }
        },
        {
            "$match": {
            "sessions.requests": { "$ne": [] }
            }
        }
    ])]
    if not traces:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No data found for this client")
    return traces

async def get_traces(collection_db):
    traces = [trace_handler(trace) async for trace in collection_db.aggregate([
        {"$unwind": "$sessions" },
        {
            "$project": {
                "_id":0, 
                "client_id":1, 
                "sessions.requests": {
                    "$filter": {
                        "input": "$sessions.requests",
                        "as": "request",
                        "cond": {"$ne": ["$$request.request_tag", "Outliers"] }
                    }
                }
            }
        },
        {
            "$match": {
            "sessions.requests": { "$ne": [] }
            }
        }
    ])]
    if not traces:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No data found")
    return traces


# Get all clients's traces
@router.get("/clients_traces/", status_code=status.HTTP_200_OK)
async def get_clients_traces(username: str, collection: str):
    await user_exists(username)
    collection_db = await collection_exists(username, collection)
    await get_traces(collection_db)

# Get unique trace number
@router.get("/unique_trace/", status_code=status.HTTP_200_OK)
async def get_unique_trace_number(username: str, collection: str):
    await user_exists(username)
    collection_db = await collection_exists(username, collection)
    trace_list = await get_traces(collection_db)
    unique_trace = list()
    for trace in trace_list:
        trace_tags = trace.split(';')[1]
        if not unique_trace.__contains__(trace_tags):
            unique_trace.append(trace_tags)
    return {"Trace number":len(trace_list), "Unique Trace Number" : len(unique_trace)}

async def get_popularity(trace_list):
    popularity = dict()
    for trace in trace_list:
        trace_tags = trace.split(';')[1]
        if not popularity.keys().__contains__(trace_tags):
            popularity[trace_tags] = 1
        else:
            popularity[trace_tags] += 1
    return popularity

# Get popularity action
@router.get("/popularity_action/", status_code=status.HTTP_200_OK)
async def get_popularity_action(username: str, collection: str):
    await user_exists(username)
    collection_db = await collection_exists(username, collection)
    trace_list = await get_traces(collection_db)
    await get_popularity(trace_list)

# Get most popular action
@router.get("/most_popular_action/", status_code=status.HTTP_200_OK)
async def get_most_popular_action(username: str, collection: str, number:int | None=5):
    await user_exists(username)
    collection_db = await collection_exists(username, collection)
    trace_list = await get_traces(collection_db)
    popularity = await get_popularity(trace_list)
    return nlargest(number, popularity, key=popularity.get)

# Get less popular action
@router.get("/less_popular_action/", status_code=status.HTTP_200_OK)
async def get_less_popular_action(username: str, collection: str, number:int | None=5):
    await user_exists(username)
    collection_db = await collection_exists(username, collection)
    trace_list = await get_traces(collection_db)
    popularity = await get_popularity(trace_list)
    return nsmallest(number, popularity, key=popularity.get)

async def unique_trace_number(collection_db):
    trace_list = await get_traces(collection_db)
    unique_trace = list()
    for trace in trace_list:
        trace_tags = trace.split(';')[1]
        if not unique_trace.__contains__(trace_tags):
            unique_trace.append(trace_tags)
    return len(trace_list), len(unique_trace)

# Get average action
@router.get("/average_action/", status_code=status.HTTP_200_OK)
async def get_average_action(username: str, collection: str):
    await user_exists(username)
    collection_db = await collection_exists(username, collection)
    trace_len, unique_trace = await unique_trace_number(collection_db)
    #return {"Average " : unique_trace/trace_len}
    return {"Average " : trace_len/unique_trace}

# Get action's number
@router.get("/action_number/", status_code=status.HTTP_200_OK)
async def get_action_number(username: str, collection: str):
    await user_exists(username)
    collection_db = await collection_exists(username, collection)
    trace_list = await get_traces(collection_db)
    cpt = 0
    for trace in trace_list:
        actions = trace.split(';')[1].split(',')
        cpt+=len(actions)
    return cpt


# Get stat string
@router.get("/stat_string/", status_code=status.HTTP_200_OK)
async def get_stat_string(username: str, collection: str):
    await user_exists(username)
    collection_db = await collection_exists(username, collection)
    trace_len, unique_trace = await unique_trace_number(collection_db)
    average = trace_len/unique_trace
    return {"Total":trace_len.__str__(),"Unique":unique_trace.__str__(),"Average":average.__str__()}
