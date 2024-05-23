import tempfile
from typing import Union, List, Annotated, Dict, Any
from fastapi import FastAPI, UploadFile, File, APIRouter, HTTPException, Query, Request, Depends, Body
from clustering.main import (trace_based_clustering, vector_based_clustering, feature_based_clustering,
                             fss_meanshift, fss_euclidean_distance)
import io
import os
from .collection import create_collection
from ..models.collection import Collection_Create_Model, Collection_Model
from ..models.users import User_Model
from ..security import get_current_active_user
from ..models.cluster_params import ClusteringMethod, ClusteringParams, DistanceMeasure, VectorRepresentation, LinkageCriteria
from ..models.cluster_params import ClusteringMethodFss, FssDistanceMeasure,FssClusteringParams
from src.clustering_utils import post_clusters, empty_directory
import pandas as pd

router = APIRouter(
    prefix="/clustering",
    tags=["clustering"]
)


@router.post("/trace/")
async def trace_based(
        current_user: Annotated[User_Model, Depends(get_current_active_user)],
        algorithm: ClusteringMethod, linkage: LinkageCriteria,params: ClusteringParams = Depends(), file: UploadFile = File(...)):
    """
        Trace based clustering using levenshtein distance measure, and choosing the clustering algorithm and
        the parameters for each algorithm

    """
    try:
        file_content = await file.read()
        # Decode file content
        decode = io.StringIO(file_content.decode('utf-8'))
        params.linkage = linkage.lower()
        # Perform trace-based clustering
        result = trace_based_clustering(decode, algorithm, params)
        # save the resulting log files in the user's collection
        files_paths = []
        log_directory = "temp/logs"
        for filename in os.listdir(log_directory):
            if filename.startswith("cluster_log_"):
                file_path = os.path.join(log_directory, filename)
                files_paths.append(file_path)
        print("files pathh ",files_paths)
        # await post_clusters(files_paths, params.collection, current_user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feature_based/")
async def vector_representation(
        # current_user: Annotated[User_Model, Depends(get_current_active_user)],
        clustering_method: ClusteringMethod, linkage: LinkageCriteria, vector_representation: VectorRepresentation, distance : DistanceMeasure,
        params: ClusteringParams = Depends(), file: UploadFile = File(...)):
    """
        Feature based clustering by representing the data as binary vectors, frequency vectors or relative
        frequency vectors

    """
    file_content = await file.read()
    decode = io.StringIO(file_content.decode('utf-8'))
    params.linkage = linkage.lower()
    params.distance = distance.lower()
    #perform feature based clustering based on the vector representation and algorithm chosen by the user
    result, nb = vector_based_clustering(decode, vector_representation.lower(), clustering_method, params)
    # save the resulting log files in the user's collection
    files_paths = []
    log_directory = "temp/logs"
    for filename in os.listdir(log_directory):
        if filename.startswith("cluster_log_"):
            file_path = os.path.join(log_directory, filename)
            files_paths.append(file_path)
    print("files pathh ", files_paths)
    # await post_clusters(files_paths, params.collection, current_user)
    result["Number of traces"] = nb["Number of traces"]
    return result


@router.post("/feature_based/fss")
async def fss_encoding(
        clustering_method: ClusteringMethodFss, linkage: LinkageCriteria,
        params: FssClusteringParams = Depends(), file: UploadFile = File(...)):
    """
     Feature based clustering where the data are encoded using the improved FSS encoding approach
     clustering methods can be:
        Agglomerative, DBSCAN, Meanshift with any distance measure and parameters/ or
        Agglomerative with Ward linkage and Euclidean distance

    """
    file_content = await file.read()
    decode = io.StringIO(file_content.decode('utf-8'))
    params.linkage = linkage.lower()
    # chosing the clustering algorithm and performing clustering on fss encoding vectors
    if linkage == "Ward" and params.distance == "Euclidean":
        result,nb = fss_euclidean_distance(decode, params.nbr_clusters, params.min_support, params.min_length)
    else:
        result,nb = feature_based_clustering(decode, clustering_method.lower(), params, params.min_support, params.min_length)

    files_paths = []
    log_directory = "temp/logs"
    for filename in os.listdir(log_directory):
        if filename.startswith("cluster_log_"):
            file_path = os.path.join(log_directory, filename)
            files_paths.append(file_path)
    print("files pathh ", files_paths)
    result["Number of traces"] = nb["Number of traces"]
    return result

@router.post("/feature_based/fss_meanshift")
async def fss_meanshift_algo(
        distance: DistanceMeasure,
        min_support:int = 80 ,min_length: int = 0 , file: UploadFile = File(...)):
    """
     Feature based clustering using Meanshift algorithm, the distance measures used can be  Jaccard
    Hamming or Cosine distance
    """
    file_content = await file.read()
    decode = io.StringIO(file_content.decode('utf-8'))
    result, nb = fss_meanshift(decode, distance.lower(), min_support, min_length)
    files_paths = []
    log_directory = "temp/logs"
    for filename in os.listdir(log_directory):
        if filename.startswith("cluster_log_"):
            file_path = os.path.join(log_directory, filename)
            files_paths.append(file_path)

    print("files pathh ", files_paths)
    result["Number of traces"] = nb["Number of traces"]
    result["logs_path"] = files_paths
    return result
