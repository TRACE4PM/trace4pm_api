from datetime import date, datetime
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated
from ..models.users import User_Model
from ..security import get_current_active_user

from ..collection_utils import collection_exists
from ..users_utils import user_exists

router = APIRouter(prefix="/requests", tags=["requests"])


# Get all client's requests
@router.get("/", status_code=status.HTTP_200_OK)
async def get_clients_requests(collection: str, client_id: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    requests = [
        request
        async for request in collection_db.find(
            {"client_id": client_id},
            {"_id": 0, "client_id": 1, "country": 1, "sessions": {"requests": 1}},
        )
    ]
    if not requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Request found for this client",
        )
    return requests


# Get all clients's requests for a country
@router.get("/country/", status_code=status.HTTP_200_OK)
async def get_country_requests(collection: str, country_name: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    requests = [
        request
        async for request in collection_db.find(
            {"country": {'$regex': country_name, "$options": "i" }},
            {
                "_id": 0,
                "client_id": 1,
                "country": 1,
                "city": 1,
                "sessions": {"requests": 1},
            },
        )
    ]
    if not requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Request found for this country",
        )
    return requests


# Get all clients's requests for a city
@router.get("/city/", status_code=status.HTTP_200_OK)
async def get_city_requests(collection: str, city_name: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    requests = [
        request
        async for request in collection_db.find(
            {"city": {'$regex': city_name, "$options": "i" }},
            {"_id": 0, "client_id": 1, "city": 1, "sessions": {"requests": 1}},
        )
    ]
    if not requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Request found for this city",
        )
    return requests


# Get all requests for a specific date
@router.get("/req_date/", status_code=status.HTTP_200_OK)
async def get_requests_by_date(collection: str, request_date: date, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    date_format = "%Y-%m-%d:%H:%M:%S %z"
    try:
        start_date = datetime.strptime(
            str(request_date) + ":00:00:00 +0200", date_format
        )
        end_date = datetime.strptime(str(request_date) + ":23:59:59 +0200", date_format)
        requests = [
            request
            async for request in collection_db.find(
                {
                    "sessions.requests.request_time": {
                        "$gte": start_date,
                        "$lte": end_date,
                    }
                },
                {"_id": 0},
            )
        ]
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Invalid date format"
        )
    if not requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Request found for this date",
        )
    return requests


# Get all requests for a specific date interval
@router.get("/date_interval/", status_code=status.HTTP_200_OK)
async def get_requests_by_date_interval(
    collection: str, start_date: date, end_date: date, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    date_format = "%Y-%m-%d:%H:%M:%S %z"
    start_date = datetime.strptime(str(start_date) + ":00:00:00 +0200", date_format)
    end_date = datetime.strptime(str(end_date) + ":23:59:59 +0200", date_format)
    requests = [
        request
        async for request in collection_db.find(
            {"sessions.requests.request_time": {"$gte": start_date, "$lte": end_date}},
            {"_id": 0},
        )
    ]
    if not requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Request found for this date interval",
        )
    return requests
