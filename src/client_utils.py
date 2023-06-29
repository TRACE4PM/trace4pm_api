from fastapi.encoders import jsonable_encoder

from parser.models.client import Client_Model


async def get_clients_from_collection(collection) -> list[Client_Model]:
    """Function to get all the clients from a collection(database)

    Args:
        collection (collection_object): collection(database) to get the clients from

    Returns:
        list[Client_Model]: list of clients
    """
    list_client = []
    async for document in collection.find({}, {"_id": 0}):
        list_client.append(Client_Model(**document))
    return list_client


async def post_clients_in_collection(
    list_clients: list[Client_Model], collection_db
) -> None:
    """Function to post a list of clients in a collection(database)

    Args:
        list_clients (list[Client_Model]): list of clients to post in the collection
        collection (collection_object): collection(database) to post the clients in
    """
    await collection_db.insert_many(jsonable_encoder(list_clients))
