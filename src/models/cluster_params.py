from enum import Enum
from typing import Optional
from ..base import Base_model


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


class ClusteringParams(Base_model):
    eps: Optional[float] = None
    min_samples: Optional[int] = None
    n_clusters: Optional[int] = None
    linkage: Optional[str] = None
    distance: Optional[str] = None
    collection: Optional[str] = None

