from fastapi import FastAPI
#from fastapi.testclient import TestClient

from ..api.routers import client, collection, files, request, tags, users, stats

apptest = FastAPI()

apptest.include_router(users.router)
apptest.include_router(collection.router)
apptest.include_router(files.router)
apptest.include_router(tags.router)
apptest.include_router(client.router)
apptest.include_router(request.router)
apptest.include_router(stats.router)

#test_client = TestClient(apptest)