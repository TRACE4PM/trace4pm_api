from typing import Dict

from ..base import Base_model



class ActionFrequencyResponse(Base_model):
    client_id: str
    action_frequency: Dict[str, int]

class ClientSessionDurationResponse(Base_model):
    client_id: str
    total_duration_seconds: float
    total_duration_days: float
    total_duration_weeks: float