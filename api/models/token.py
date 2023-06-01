from api.base import Base_model


class Token(Base_model):
    access_token: str
    token_type: str


class TokenData(Base_model):
    username: str
