from enum import Enum
from typing import Optional
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
    distance: Optional[str] = None
    collection: Optional[str] = None
