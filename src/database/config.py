import motor.motor_asyncio

MONGO_DETAILS = "mongodb://mongodb:mongo@database:27017"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.trace_logs

user_collection = database.get_collection("users")
