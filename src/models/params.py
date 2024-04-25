from src.base import Base_model
from enum import Enum

class MiningResult(Base_model):
    Fitness: dict
    Precision: float
    Generalization: float
    Simplicity: float


class Quality_Type(str, Enum):
    token = "Token based"
    align = "Alignement"
