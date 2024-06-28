import csv
import io
import os
import tempfile
import zipfile
from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, Request, status, UploadFile, Response
from fastapi.responses import FileResponse
from typing import Annotated
from ..collection_utils import collection_exists
from ..models.cluster_params import ClusteringMethod, ClusteringParams, DistanceMeasure, LinkageCriteria, VectorRepresentation
from ..models.cluster_params import ClusteringMethodFss, FssClusteringParams, FssDistanceMeasure
from ..models.users import User_Model
from ..security import get_current_active_user
from clustering.main import (feature_based_clustering, fss_euclidean_distance, fss_meanshift,
                             trace_based_clustering, vector_based_clustering)
from src.clustering_utils import empty_directory, post_clusters, fetch_documents, create_csv_files, create_zip_file, create_csv_file



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
    Args:
        clustering_method: Agglomerative or DBSCAN
        linkage: Linkage criteria for Agglomerative can be Average, Complete, Single with any distance measure,
        params: parameters of each clustering algorithm
            epsilon and min_samples => DBSCAN
            n_cluster and linkage criteria => Agglomerative
        file: log file
    Returns:
        Davis bouldin score
        Number of clusters
        Silhouette score of the clustering and for each cluster
    """
    try:
        file_content = await file.read()
        # Decode file content
        decode = io.StringIO(file_content.decode('utf-8'))
        params.linkage = linkage.lower()
        # Perform trace-based clustering
        result, nb = trace_based_clustering(decode, algorithm, params)
        result["Number of traces"] = nb["Number of traces"]
        # save the resulting log files in the user's collection
        files_paths = []
        log_directory = "temp/logs"
        # retrieve the files stored in the log directory
        for filename in os.listdir(log_directory):
            if filename.startswith("cluster_log_"):
                file_path = os.path.join(log_directory, filename)
                files_paths.append(file_path)

        await post_clusters(files_paths,None, 'Trace Based Clustering', params, current_user, result)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feature_based/")
async def vector_representation(
        current_user: Annotated[User_Model, Depends(get_current_active_user)],
        clustering_method: ClusteringMethod, linkage: LinkageCriteria, vector_representation: VectorRepresentation, distance : DistanceMeasure,
        params: ClusteringParams = Depends(), file: UploadFile = File(...)):
    """
        Feature based clustering by representing the data as binary vectors, frequency vectors or relative
        frequency vectors
    Args:
        clustering_method: Agglomerative or DBSCAN
        linkage: Linkage criteria for Agglomerative can be Average, Complete, Single with any distance measure,
        vector_representation: convert the trace to a vector representation either with Binary, Frequency based, or Relative frequency
        representation
        distance: distance measure for the clustering, either Hamming, Jaccard or Cosine distance
        params: parameters of each clustering algorithm
            epsilon and min_samples => DBSCAN
            n_cluster and linkage criteria => Agglomerative
        file: log file
    Returns:
        Davis bouldin score
        Number of clusters
        Silhouette score of the clustering and for each cluster

    """
    try:
        file_content = await file.read()
        decode = io.StringIO(file_content.decode('utf-8'))
        params.linkage = linkage.lower()
        params.distance = distance.lower()
        #perform feature based clustering based on the vector representation and algorithm chosen by the user
        result, nb = vector_based_clustering(decode, vector_representation.lower(), clustering_method, params)
        result["Number of traces"] = nb["Number of traces"]
        # save the resulting log files in the user's collection
        files_paths = []
        log_directory = "temp/logs"
        for filename in os.listdir(log_directory):
            if filename.startswith("cluster_log_"):
                file_path = os.path.join(log_directory, filename)
                files_paths.append(file_path)
        await post_clusters(files_paths, None, 'Feature Based Clustering', params, current_user, result)
        return result
    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# TODO:
#  FSS encoding takes too much time, trying to fix it
@router.post("/feature_based/fss")
async def fss_encoding(
    current_user: Annotated[User_Model, Depends(get_current_active_user)],
        # clustering_method: ClusteringMethodFss, linkage: LinkageCriteria,
        collection : str,
        nbr_clusters : int, min_support: int = 99, min_length: int = 9,file: UploadFile = File(...)):
    """
    Feature based clustering where the data are encoded using the improved FSS encoding approach

    Args:
       file: log file
    Returns:
        Davis bouldin score
        Number of clusters
        Silhouette score of the clustering and for each cluster

    """
    try :

        file_content = await file.read()
        decode = io.StringIO(file_content.decode('utf-8'))
        # chosing the clustering algorithm and performing clustering on fss encoding vectors
        # if linkage == "Ward" and params.distance == "Euclidean":
        nb = fss_euclidean_distance(decode, nbr_clusters, min_support, min_length)
        # else:
        #     result,nb = feature_based_clustering(decode, clustering_method.lower(), params, params.min_support, params.min_length)
        # result["Number of traces"] = nb["Number of traces"]
        # result["Number unique traces"] = nb["Number unique traces"]
        files_paths = []
        log_directory = "temp/logs"
        for filename in os.listdir(log_directory):
            if filename.startswith("cluster_log_"):
                file_path = os.path.join(log_directory, filename)
                files_paths.append(file_path)
        await post_clusters(files_paths, collection, current_user)
        return nb
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# NOTE: Will probably remove this approach later

# @router.post("/feature_based/fss_meanshift")
# async def fss_meanshift_algo(
#         current_user: Annotated[User_Model, Depends(get_current_active_user)],
#         distance: DistanceMeasure, collection: str,
#         min_support:int = 99 ,min_length: int = 9 , file: UploadFile = File(...)):
#     """
#          Feature based clustering using Meanshift algorithm, the distance measures used can be  Jaccard
#     Hamming or Cosine distance
#
#     Args:
#         distance: Distance measure, either Jaccard, Cosine, or Hamming distance
#         collection: name of the collection where we will store the resulting clusters
#         min_support/min_length: Fss encoding parameters to calculate the frequent subsequences
#
#         file: log file
#
#     Returns:
#         Davis bouldin score
#         Number of clusters
#         Silhouette score of the clustering and for each cluster
#
#
#     """
#     try:
#         file_content = await file.read()
#         decode = io.StringIO(file_content.decode('utf-8'))
#         result, nb = fss_meanshift(decode, distance.lower(), min_support, min_length)
#         result["Number of traces"] = nb["Number of traces"]
#         result["Number unique traces"] = nb["Number unique traces"]
#         files_paths = []
#         log_directory = "temp/logs"
#         for filename in os.listdir(log_directory):
#             if filename.startswith("cluster_log_"):
#                 file_path = os.path.join(log_directory, filename)
#                 files_paths.append(file_path)
#         await post_clusters(files_paths, collection, current_user)
#
#         return result
#     except HTTPException as e:
#         raise e
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#

@router.get("/get_clusters")
async def get_clusters_func( collection: str,
        current_user: Annotated[User_Model, Depends(get_current_active_user)],
):
    """Route to get a json object from a collection

    Args:
        collection (str): collection name

    Returns:
        dict: json object
    """
    try:
        # Check if the collection exists
        collection_db = await collection_exists(current_user.username, collection)
        documents = await fetch_documents(collection_db)

        # Create a directory to store the CSV files
        directory = "src/temp/clusters"
        file_paths = create_csv_files(documents, directory)

        return {"message": "Documents have been saved as CSV files.", "file_paths": file_paths}

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_cluster_file")
async def get_file( collection: str, cluster_id : int,
        current_user: Annotated[User_Model, Depends(get_current_active_user)],
):

    try:
        # Check if the collection exists
        collection_db = await collection_exists(current_user.username, collection)
        documents = await fetch_documents(collection_db)

        # Create a directory to store the CSV files
        csv_data = create_csv_file(documents, cluster_id)

        response = Response(content=csv_data, media_type="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename=cluster_{cluster_id}.csv"
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


