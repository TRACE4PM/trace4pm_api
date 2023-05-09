from fastapi.encoders import jsonable_encoder

from api.models.client import Client_Model


# Function to get a dict {client_id:Client_Model} of clients object from the collection(database)
async def get_clients_from_collection(collection) -> dict:
    dict_clients = {}
    async for document in collection.find({}, {"_id": 0}):
        client = Client_Model(**document)
        dict_clients[client.client_id] = client

    return dict_clients


# Function to post a client object in the collection(database)
async def post_clients_in_collection(list_clients: list[Client_Model], collection) -> None:
    await collection.insert_many(jsonable_encoder(list_clients))
