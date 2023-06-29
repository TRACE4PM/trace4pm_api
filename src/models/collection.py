from ..base import Base_model


class Collection_Base_Model(Base_model):
    name: str
    description: str | None = None


class Collection_Model(Collection_Base_Model):
    created_at: str | None = None
    files_hash: list[str] | None = None


class Collection_Create_Model(Collection_Base_Model):
    pass

    class Config:
        pass
