# from ..base import Base_model
from pydantic import BaseModel, Field, ValidationError
from fastapi import UploadFile, File
from typing import Literal, Dict
from enum import Enum
from typing import Optional, Union
from ..models.collection import Collection_Create_Model, Collection_Model
from ..models.users import User_Model


class ClusteringMethod(str, Enum):
    Agglomerative = "Agglomerative"
    DBSCAN = "DBScan"


class DistanceMeasure(str, Enum):
    Jaccard = "Jaccard"
    Hamming = "Hamming"
    Cosine = "Cosine"


class VectorRepresentation(str, Enum):
    Binary = "Binary Representation"
    Frequency = "Frequency Representation"
    RelativeFrequency = "Relative Frequency Representation"


class ClusteringParams(BaseModel):
    eps: Optional[float] = None
    min_samples: Optional[int] = None
    n_clusters: Optional[int] = None
    linkage: Optional[str] = None
    distance: Optional[str] = None
    collection: Optional[str] = None

