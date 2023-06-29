from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated
from ..models.users import User_Model
from ..security import get_current_active_user
from fastapi.encoders import jsonable_encoder
from ..users_utils import user_exists
from ..collection_utils import collection_exists
from parser.models.client import Client_Base_Model

router = APIRouter(
    prefix="/clients",
    tags=["clients"]
)


# Get all clients saved in the database without their session's information
@router.get("/", status_code=status.HTTP_200_OK, description="Get all clients's information without their session's information")
async def get_clients(collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)])->list[Client_Base_Model]:
    """This route allows to retrieve the clients's informations

    Args:
        collection (str): name of the collection containing the clients's logs

    Returns:
        list[Client_Base_Model]: The list of the clients
        code: 200
    """
    collection_db = await collection_exists(current_user.username, collection)
    clients = [client async for client in collection_db.find({}, { '_id':0,'client_id': 1, 'country': 1, 'city':1, 'user_agent':1 })]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client's log exists yet")
    return clients


# Get a client's specific information
@router.get("/{client_id}", status_code=status.HTTP_200_OK, description="Get the information of a giving client")
async def get_client(collection: str, client_id: str, current_user: Annotated[User_Model, Depends(get_current_active_user)])->Client_Base_Model:
    """This route allows to retrieve a client's informations

    Args:
        collection (str): name of the collection containing the clients's logs
        client_id (str): id of the target client

    Returns:
        Client_Base_Model: The client's information
        code: 200
    """
    collection_db = await collection_exists(current_user.username, collection)
    client = await collection_db.find_one({'client_id': client_id}, { '_id':0,'client_id': 1, 'country': 1, 'city':1, 'user_agent':1 })
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No log exists yet for this client")
    return client


# Get all clients for a specific country
@router.get("/country/", status_code=status.HTTP_200_OK, description="Get all clients's information for a giving country")
async def get_clients_by_country(collection: str, country_name: str, current_user: Annotated[User_Model, Depends(get_current_active_user)])->list[Client_Base_Model]:
    """This route allows to retrieve the clients's informations for a giving country

    Args:
        collection (str): name of the collection containing the clients's logs
        country_name (str): name of the country

    Returns:
        list[Client_Base_Model]: The list of the clients
        code: 200
    """
    collection_db = await collection_exists(current_user.username, collection)
    clients = [client async for client in collection_db.find({'country': {'$regex': country_name, "$options": "i" }}, { '_id':0,'client_id': 1, 'country': 1, 'city':1, 'user_agent':1 })]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client's log exists yet for this country")
    return clients

# Get all clients for a specific city
@router.get("/city/", status_code=status.HTTP_200_OK, description="Get all clients's information for a giving city")
async def get_clients_by_city(collection: str, city_name: str, current_user: Annotated[User_Model, Depends(get_current_active_user)])->list[Client_Base_Model]:
    """This route allows to retrieve the clients's informations for a giving city

    Args:
        collection (str): name of the collection containing the clients's logs
        city_name (str): name of the city

    Returns:
        list[Client_Base_Model]: The list of the clients
        code: 200
    """
    collection_db = await collection_exists(current_user.username, collection)
    clients = [client async for client in collection_db.find({'city': {'$regex': city_name, "$options": "i" }}, { '_id':0,'client_id': 1, 'country': 1, 'city':1, 'user_agent':1 })]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client's log exists yet for this city")
    return clients

# Get the number of clients grouped by country
@router.get("/stats/country/group/", status_code=status.HTTP_200_OK, description="Get the number of clients grouped by country")
async def get_number_of_clients_grouped_by_country(collection: str, current_user: Annotated[User_Model, Depends(get_current_active_user)])->list:
    """This route allows to retrieve the number of clients grouped by country

    Args:
        collection (str): name of the collection containing the clients's logs

    Returns:
        list: The list of the different countries with their respective number of clients
        code: 200
    """
    collection_db = await collection_exists(current_user.username, collection)
    clients = [client async for client in collection_db.aggregate([{'$group': {'_id': "$country", 'Total': { '$count': {}}}}, 
                                                                   { '$sort': {'_id': 1}},
                                                                   {'$project':{'_id': 0, 'Country': '$_id', 'Total': 1}}])]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client's log exists yet for this country")
    return clients

# Get the number of clients for a specific country grouped by city
@router.get("/stats/country/group_city/", status_code=status.HTTP_200_OK, description="Get the number of clients grouped by city for a specific country")
async def get_number_of_clients_grouped_by_city(collection: str, country_name: str, current_user: Annotated[User_Model, Depends(get_current_active_user)])->list:
    """This route allows to retrieve the number of clients grouped by city for a giving country

    Args:
        collection (str): name of the collection containing the clients's logs
        country_name (str): name of a giving country 

    Returns:
        list: The list of the different cities with their respective number of clients
        code: 200
    """
    collection_db = await collection_exists(current_user.username, collection)
    clients = [client async for client in collection_db.aggregate([{'$match': {'country': {'$regex': country_name, "$options": "i" }}}, 
                                                                   {'$group': {'_id': "$city", 'Total': { '$count': {}}}}, 
                                                                   {'$sort': {'_id': 1}},
                                                                   {'$project':{'_id': 0,'City': '$_id', 'Total': 1}}])]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client's log exists yet for this country")
    return clients

# Get the number of clients for a specific country
@router.get("/stats/country/", status_code=status.HTTP_200_OK, description="Get the number of clients for a specific country")
async def get_number_of_clients_for_a_country(collection: str, country_name: str, current_user: Annotated[User_Model, Depends(get_current_active_user)])->dict:
    """This route allows to retrieve the number of clients for a giving country

    Args:
        collection (str): name of the collection containing the clients's logs
        country_name (str): name of a giving country 

    Returns:
        dict: The total number of clients
        code: 200
    """
    collection_db = await collection_exists(current_user.username, collection)
    clients = [client async for client in collection_db.aggregate([{'$match': {'country': {'$regex': country_name, "$options": "i" }}}, {'$count': 'Total'}])]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client's log exists yet for this country")
    return clients[0]

# Get the number of clients for a specific city
@router.get("/stats/city/", status_code=status.HTTP_200_OK, description="Get the number of clients for a specific city")
async def get_number_of_clients_for_a_city(collection: str, city_name: str, current_user: Annotated[User_Model, Depends(get_current_active_user)])->dict:
    """This route allows to retrieve the number of clients for a giving city

    Args:
        collection (str): name of the collection containing the clients's logs
        country_name (str): name of a giving city 

    Returns:
        dict: The total number of clients
        code: 200
    """
    collection_db = await collection_exists(current_user.username, collection)
    clients = [client async for client in collection_db.aggregate([{'$match': {'city': {'$regex': city_name, "$options": "i" }}}, {'$count': 'Total'}])]
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Client's log exists yet for this city")
    return clients[0]