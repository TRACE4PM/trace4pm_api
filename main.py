from fastapi import FastAPI

from api.routers import client, collection, files, request, tags, users

app = FastAPI()

app.include_router(users.router)
app.include_router(collection.router)
app.include_router(files.router)
app.include_router(tags.router)
app.include_router(client.router)
app.include_router(request.router)
