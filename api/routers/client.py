from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder

from api.models.client import Client_Get_Model
from database.config import collection_users_logs as users_logs

router = APIRouter(
    prefix="/clients",
    tags=["clients"]
)


# Get all clients saved in the database without their session's information
@router.get("/", status_code=status.HTTP_200_OK)
async def get_clients():
    clients = [client async for client in users_logs.find({}, {'_id': 0, 'client_id': 1, 'country': 1, 'city': 1, 'user_agent': 1})]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client exists yet")
    return clients


# Get a client's specific information
@router.get("/{client_id}", status_code=status.HTTP_200_OK)
async def get_client(client_id: str):
    client = await users_logs.find_one({'client_id': client_id}, {'_id': 0, 'client_id': 1, 'country': 1, 'city': 1, 'user_agent': 1})
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client exists yet")
    return client


# Get all clients for a specific country
@router.get("/country/{country_name}", status_code=status.HTTP_200_OK)
async def get_clients_by_country(country_name: str):
    clients = [client async for client in users_logs.find({'country': country_name}, {'_id': 0, 'client_id': 1, 'country': 1, 'city': 1, 'user_agent': 1})]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client exists yet for this country")
    return clients


# Get all clients for a specific city
@router.get("/city/{city_name}", status_code=status.HTTP_200_OK)
async def get_clients_by_city(city_name: str):
    clients = [client async for client in users_logs.find({'city': city_name}, {'_id': 0, 'client_id': 1, 'country': 1, 'city': 1, 'user_agent': 1})]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client exists yet for this city")
    return clients


# Get the number of clients for a specific country grouped by city
@router.get("/stats/country/{country_name}", status_code=status.HTTP_200_OK)
async def get_number_of_clients_grouped_by_city(country_name: str):
    clients = [client async for client in users_logs.aggregate([{'$match': {'country': country_name}}, {'$group': {'_id': "$city", 'Total': {'$count': {}}}}, {'$sort': {'_id': 1}}])]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client exists yet for this country")
    return clients


# Get the number of clients for a specific city
@router.get("/stats/city/{city_name}", status_code=status.HTTP_200_OK)
async def get_number_of_clients_for_a_city(city_name: str):
    clients = [client async for client in users_logs.aggregate([{'$match': {'city': city_name}}, {'$count': 'Total'}])]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client exists yet for this city")
    return clients[0]
