from api.base import Base_model
from api.models.request import Request_Model


class Session_Model(Base_model):
    session_id: float | None = None
    requests: list[Request_Model] = []
