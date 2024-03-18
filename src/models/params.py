from src.base import Base_model


class MiningResult(Base_model):
    Fitness: dict
    Precision: float
    Generalization: float
    Simplicity: float