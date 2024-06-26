from enum import Enum
from typing import Optional
from datetime import datetime
from ..base import Base_model


class ClusteringMethod(str, Enum):
    Agglomerative = "Agglomerative"
    DBSCAN = "DBSCAN"


class ClusteringMethodFss(str, Enum):
    Agglomerative = "Agglomerative"
    DBSCAN = "DBSCAN"
    Meanshift = "Meanshift"


class DistanceMeasure(str, Enum):
    Jaccard = "Jaccard"
    Hamming = "Hamming"
    Cosine = "Cosine"

class LinkageCriteria(str, Enum):
    Single = "Single"
    Complete = "Complete"
    Average = "Average"
    Ward = "Ward"


class VectorRepresentation(str, Enum):
    Binary = "Binary Representation"
    Frequency = "Frequency Representation"
    RelativeFrequency = "Relative Frequency Representation"


class ClusteringParams(Base_model):
    """
           epsilon and min_samples parameters for DBScan algorithm
           nbr_cluster and linkage criteria for Agglomerative algorithm
           distance: distance measure for feature based clustering,
       """
    epsilon: Optional[float] = None
    min_samples: Optional[int] = None
    nbr_clusters: Optional[int] = None
    linkage: Optional[str] = None
    distance:Optional[str] = None
    collection: Optional[str] = None


class FssDistanceMeasure(str, Enum):
    Jaccard = "Jaccard"
    Hamming = "Hamming"
    Cosine = "Cosine"
    Euclidean = "Euclidean"


class FssClusteringParams(Base_model):
    """
        epsilon and min_samples parameters for dbscan algorithm
        nbr_cluster and linkage critetia for agglomerative algorithm
        distance: distance measure for feature based clustering,
    """
    distance: Optional[FssDistanceMeasure]
    epsilon: Optional[float] = None
    min_samples: Optional[int] = None
    nbr_clusters: Optional[int] = None
    linkage: Optional[str] = None
    min_support: Optional[int] = 99
    min_length: Optional[int] = 9
    collection: Optional[str] = None


class ClientSessionDurationResponse(Base_model):
    client_id: str
    total_duration_seconds: float