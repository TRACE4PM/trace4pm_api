from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated
from ..models.users import User_Model
from ..security import get_current_active_user
from fastapi.encoders import jsonable_encoder
from ..users_utils import user_exists
from ..collection_utils import collection_exists

router = APIRouter(
    prefix="/clients",
    tags=["clients"]
)


# Get all clients saved in the database without their session's information
@router.get("/", status_code=status.HTTP_200_OK)
async def get_clients(collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    clients = [client async for client in collection_db.find({}, { '_id':0,'client_id': 1, 'country': 1, 'city':1, 'user_agent':1 })]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client's log exists yet")
    return clients


# Get a client's specific information
@router.get("/{client_id}", status_code=status.HTTP_200_OK)
async def get_client(collection: str, client_id: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    client = await collection_db.find_one({'client_id': client_id}, { '_id':0,'client_id': 1, 'country': 1, 'city':1, 'user_agent':1 })
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No log exists yet for this client")
    return client


# Get all clients for a specific country
@router.get("/country/", status_code=status.HTTP_200_OK)
async def get_clients_by_country(collection: str, country_name: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    clients = [client async for client in collection_db.find({'country': country_name}, { '_id':0,'client_id': 1, 'country': 1, 'city':1, 'user_agent':1 })]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client's log exists yet for this country")
    return clients

# Get all clients for a specific city
@router.get("/city/", status_code=status.HTTP_200_OK)
async def get_clients_by_city(collection: str, city_name: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    clients = [client async for client in collection_db.find({'city': city_name}, { '_id':0,'client_id': 1, 'country': 1, 'city':1, 'user_agent':1 })]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client's log exists yet for this city")
    return clients

# Get the number of clients for a specific country grouped by city
@router.get("/stats/country/", description="Get the number of clients grouped by city for a specific country", status_code=status.HTTP_200_OK)
async def get_number_of_clients_grouped_by_city(collection: str, country_name: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    clients = [client async for client in collection_db.aggregate([{'$match': {'country': country_name}}, {'$group': {'_id': "$city", 'Total': { '$count': {}}}}, { '$sort': {'_id': 1}}])]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client's log exists yet for this country")
    return clients

# Get the number of clients for a specific city
@router.get("/stats/city/", status_code=status.HTTP_200_OK)
async def get_number_of_clients_for_a_city(collection: str, city_name: str, current_user: Annotated[User_Model, Depends(get_current_active_user)]):
    collection_db = await collection_exists(current_user.username, collection)
    clients = [client async for client in collection_db.aggregate([{'$match': {'city': city_name}}, {'$count': 'Total'}])]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client's log exists yet for this city")
    return clients[0]