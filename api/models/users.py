from api.base import Base_model
from api.models.collection import Collection_Model


class User_Base_Model(Base_model):
    username: str
    firstname: str | None = None


class User_Model(User_Base_Model):
    collections: list[Collection_Model] = []
    disabled: bool | None = None

    class config:
        pass


# Model which is stored in the database
class User_inDB_Model(User_Model):
    hashed_password: str


# Model which is used to create a user
class User_Create_Model(User_Base_Model):
    plain_password: str
