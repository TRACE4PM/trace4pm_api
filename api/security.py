from datetime import datetime, timedelta
from typing import Annotated
from api.models.users import User_inDB_Model, User_Model
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from database.config import database
from api.models.token import Token, TokenData


# Define the secret key
SECRET_KEY = "097a625b1090eda91a7f5474c780b2dc355d72e9b2e294fbc357a8a306189fd0"
# Define the algorithm used to sign the JWT
ALGORITHM = "HS256"
# Define the access token expiration time
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# Define the password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Define the OAuth2 scheme, and the tokenUrl
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Define the collection
collection_users = database.get_collection("users")


def verify_password(plain_password: str, hashed_password: str):
    """Check if the password is correct

    Args:
        plain_password (str): plain text password
        hashed_password (str): hashed password

    Returns:
        bool: True if the password is correct, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


async def get_user(username: str) -> User_inDB_Model:
    user = User_inDB_Model(**await collection_users.find_one({"username": username}))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username doesn't exist"
        )
    return user


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create an access token

    Args:
        data (dict): The data to encode
        expires_delta (timedelta | None, optional): expires time. Defaults to None.

    Returns:
        str: The access token
    """
    to_encode = data.copy()
    # Define the expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    # If the expiration time is not defined, use the default value of 15 minutes
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Get the current user (if the token is valid)

    Args:
        token (Annotated[str, Depends): The token

    Returns:
        User_inDB_Model: The current user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # type: ignore
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User_Model, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
