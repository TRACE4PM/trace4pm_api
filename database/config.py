import motor.motor_asyncio

MONGO_DETAILS = "mongodb://mongodb:mongo@localhost:27017"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.trace_logs

collection_users_logs = database.get_collection("users_logs")
