
from pydantic import BaseModel

class Event_Model(BaseModel):
    timestamp: str
    action: str
    session_id: str
