from fastapi import Depends, FastAPI

from src.routers import client, collection, files, request, stats, tags, token, users, discover, clustering, session
from src.security import oauth2_scheme
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost",

]

# Add CORS middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


oauth2_scheme = Depends(oauth2_scheme)

app.include_router(token.router)
app.include_router(users.router)
app.include_router(collection.router)
app.include_router(files.router)
app.include_router(tags.router)
app.include_router(client.router)
app.include_router(request.router)
app.include_router(stats.router)
app.include_router(discover.router)
app.include_router(clustering.router)
app.include_router(session.router)

