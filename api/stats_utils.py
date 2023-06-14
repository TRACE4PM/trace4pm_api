from fastapi import APIRouter, HTTPException, status, Depends
from .tags_utils import trace_handler
from heapq import nlargest
from heapq import nsmallest

async def get_traces(collection_db):
    traces = [
        trace_handler(trace)
        async for trace in collection_db.aggregate(
            [
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
            status_code=status.HTTP_404_NOT_FOUND, detail="No data found"
        )
    return traces

async def get_popularity(trace_list):
    popularity = dict()
    for trace in trace_list:
        trace_tags = trace.split(";")[1]
        if not popularity.keys().__contains__(trace_tags):
            popularity[trace_tags] = 1
        else:
            popularity[trace_tags] += 1
    return popularity

async def unique_trace_number(collection_db):
    trace_list = await get_traces(collection_db)
    unique_trace = list()
    for trace in trace_list:
        trace_tags = trace.split(";")[1]
        if not unique_trace.__contains__(trace_tags):
            unique_trace.append(trace_tags)
    return len(trace_list), len(unique_trace)

async def get_actions(collection_db):
    trace_list = await get_traces(collection_db)
    action_list = list()
    for trace in trace_list:
        action_list.extend(trace.split(";")[1].split(","))
    return action_list
        

async def unique_action_infos(collection_db):
    action_list = await get_actions(collection_db)
    unique_action = list()
    for action in action_list:
        if not unique_action.__contains__(action):
            unique_action.append(action)
            print(action)
    return len(action_list), unique_action

async def popularity_action(action_list):
    popularity = dict()
    for action in action_list:
        if not popularity.keys().__contains__(action):
            popularity[action] = 1
        else:
            popularity[action] += 1
    return popularity

async def action_number(collection_db):
    trace_list = await get_traces(collection_db)
    cpt = 0
    for trace in trace_list:
        actions = trace.split(";")[1].split(",")
        cpt += len(actions)
    return cpt