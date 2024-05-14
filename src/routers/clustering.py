from typing import Union, List, Annotated, Dict, Any
from fastapi import FastAPI, UploadFile, File, APIRouter, HTTPException, Query, Request, Depends, Body
from clustering.main import trace_based_clustering, vector_based_clustering, feature_based_clustering, fss_meanshift
import io
import os
from .collection import create_collection
from ..models.collection import Collection_Create_Model, Collection_Model
from ..models.users import User_Model
from ..security import get_current_active_user
from ..models.cluster_params import ClusteringMethod, ClusteringParams, DistanceMeasure, VectorRepresentation
from ..models.cluster_params import ClusteringMethodFss
from src.clustering_utils import post_clusters
import pandas as pd

router = APIRouter(
    prefix="/clustering",
    tags=["clustering"]
)


@router.post("/trace/")
async def trace_based(
        current_user: Annotated[User_Model, Depends(get_current_active_user)],
        algorithm: ClusteringMethod, params: ClusteringParams = Depends(), file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        # Decode file content
        decode = io.StringIO(file_content.decode('utf-8'))
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
        await post_clusters(files_paths, params.collection, current_user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feature_based/")
async def vector_representation(
        current_user: Annotated[User_Model, Depends(get_current_active_user)],
        clustering_method: ClusteringMethod, vector_representation: VectorRepresentation, distance : DistanceMeasure,
        params: ClusteringParams = Depends(), file: UploadFile = File(...)):

    file_content = await file.read()
    decode = io.StringIO(file_content.decode('utf-8'))
    params.distance = distance.lower()
    #perform feature based clustering based on the vector representation and algorithm chosen by the user
    result = vector_based_clustering(decode, vector_representation.lower(), clustering_method, params)

    # save the resulting log files in the user's collection
    files_paths = []
    log_directory = "temp/logs"
    for filename in os.listdir(log_directory):
        if filename.startswith("cluster_log_"):
            file_path = os.path.join(log_directory, filename)
            files_paths.append(file_path)
    print("files pathh ", files_paths)
    await post_clusters(files_paths, params.collection, current_user)
    return result


@router.post("/feature_based/fss")
async def fss_encoding(
        clustering_method: ClusteringMethodFss, distance: DistanceMeasure,
        params: ClusteringParams = Depends(), file: UploadFile = File(...)):

    file_content = await file.read()
    decode = io.StringIO(file_content.decode('utf-8'))
    params.distance = distance.lower()

    # chosing the clustering algorithm and performing clustering on fss encoding vectors
    if clustering_method == "Meanshift":
        result = fss_meanshift(decode, params)
    else :
        result = feature_based_clustering(decode, clustering_method, params)

    return result
