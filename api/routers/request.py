from datetime import date, datetime, timedelta

from fastapi import APIRouter, HTTPException, status

from database.config import collection_users_logs as users_logs

router = APIRouter(
    prefix="/requests",
    tags=["requests"]
)


# Get all client's requests
@router.get("/{client_id}", status_code=status.HTTP_200_OK)
async def get_clients_requests(client_id: str):
    requests = [request async for request in users_logs.find({'client_id': client_id}, {'_id': 0, 'client_id': 1, 'country': 1, 'sessions': {'requests': 1}})]
    if not requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Request found for this client")
    return requests


# Get all clients's requests for a country
@router.get("/country/{country}", status_code=status.HTTP_200_OK)
async def get_country_requests(country: str):
    requests = [request async for request in users_logs.find({'country': country}, {'_id': 0, 'client_id': 1, 'country': 1, 'city': 1, 'sessions': {'requests': 1}})]
    if not requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Request found for this country")
    return requests


# Get all clients's requests for a city
@router.get("/city/{city}", status_code=status.HTTP_200_OK)
async def get_city_requests(city: str):
    requests = [request async for request in users_logs.find({'city': city}, {'_id': 0, 'client_id': 1, 'city': 1, 'sessions': {'requests': 1}})]
    if not requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Request found for this city")
    return requests


# Get all requests for a specific date
@router.get("/req_date/", status_code=status.HTTP_200_OK)
async def get_requests_by_date(request_date: date):
    date_format = "%Y-%m-%d:%H:%M:%S %z"
    start_date = datetime.strptime(
        str(request_date) + ':00:00:00 +0200', date_format)
    end_date = datetime.strptime(
        str(request_date) + ':23:59:59 +0200', date_format)
    requests = [request async for request in users_logs.find({"sessions.requests.request_time": {'$gte': start_date, '$lte': end_date}}, {'_id': 0})]
    if not requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Request found for this date")
    return requests


# Get all requests for a specific date interval
@router.get("/date_interval/", status_code=status.HTTP_200_OK)
async def get_requests_by_date_interval(start_date: date, end_date: date):
    date_format = "%Y-%m-%d:%H:%M:%S %z"
    start_date = datetime.strptime(
        str(start_date) + ':00:00:00 +0200', date_format)
    end_date = datetime.strptime(
        str(end_date) + ':23:59:59 +0200', date_format)
    requests = [request async for request in users_logs.find({"sessions.requests.request_time": {'$gte': start_date, '$lte': end_date}}, {'_id': 0})]
    if not requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Request found for this date interval")
    return requests
