from fastapi import Depends, FastAPI

from api.routers import client, collection, files, request, tags, token, users
from api.security import oauth2_scheme

app = FastAPI()

oauth2_scheme = Depends(oauth2_scheme)

app.include_router(token.router)
app.include_router(users.router)
app.include_router(collection.router)
app.include_router(files.router)
app.include_router(tags.router)
app.include_router(client.router)
app.include_router(request.router)
