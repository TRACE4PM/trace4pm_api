from api.base import Base_model
from api.models.session import Session_Model


class Client_Base_Model(Base_model):
    client_id: str | None = None
    country: str | None = None
    city: str | None = None
    user_agent: str | None = None


class Client_Model(Client_Base_Model):
    sessions: list[Session_Model] = []

    def to_json(self):
        sessions = []
        for session in self.sessions:
            sessions.append(session.to_json())
        return {
            "client_id": self.client_id,
            "country": self.country,
            "city": self.city,
            "user_agent": self.user_agent,
            "sessions": sessions
        }


class Client_Get_Model(Client_Base_Model):
    class Config:
        schema_extra = {
            "example": {
                "client_id": "self.client_id",
                "country": "self.country",
                "city": "self.city",
                "user_agent": "self.user_agent",
            }
        }
