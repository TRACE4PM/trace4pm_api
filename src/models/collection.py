from typing import Optional, Dict

from ..base import Base_model


class Collection_Base_Model(Base_model):
    name: str
    description: str | None = None
    log_collection: bool | None = None


class Collection_Model(Collection_Base_Model):
    created_at: str | None = None
    files_hash: list[str] | None = None
    file_name: str | None = None

class Clustering_Collection_Model(Collection_Model):
    clustering_approach: str | None = None
    clustering_parameters: Optional[Dict] = None
    clustering_result: Optional[Dict] = None


class Collection_Create_Model(Collection_Base_Model):
    pass

    class Config:
        pass


class ClientSessionDurationResponse(Base_model):
    client_id: str
    average_duration_seconds: float