from ..base import Base_model
from .collection import Collection_Model


class User_Base_Model(Base_model):
    username: str
    firstname: str = None


class User_Model(User_Base_Model):
    collections: list[Collection_Model] = []

    class config:
        pass


class User_Create_Model(User_Base_Model):
    pass
