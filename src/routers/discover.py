import os
import tempfile
from typing import Annotated
from fastapi import FastAPI, UploadFile, File, APIRouter, HTTPException, Query, Request, Depends
from fastapi.responses import JSONResponse, Response, FileResponse, HTMLResponse
from discover.main import (alpha_miner_algo, alpha_algo_quality, alpha_miner_plus, alpha_miner_plus_quality,
                           freq_alpha_miner, heuristic_miner, heuristic_miner_petri,
                           inductive_miner, inductive_miner_quality, inductive_miner_tree,
                           dfg_precision, dfg_petri_quality,
                           dfg_performance, bpmn_model, process_animate)
from ..database.config import database
from ..collection_utils import collection_exists
from ..discover_utils import read_files, create_zip_file
from ..models.discover import Quality_Type
from ..models.users import User_Model
from ..security import get_current_active_user
from ..stats_utils import get_clients_action

import time
import logging
import sys


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/discovery",
    tags=["discovery"]
)


@router.post("/alpha-miner/")
async def alpha_miner_algorithm(
        current_user: Annotated[User_Model, Depends(get_current_active_user)],
        collection: str,
        case_name: str = "client_id",
        concept_name: str = "action",
        timestamp: str = 'timestamp', separator: str = ";",
      ):
    """
          Applying Alpha Miner algorithm on a log file and saving the model in a png file
        Args:
            separator,timestamp, concept_name,case_name: columns of the csv file
            file: csv or xes log file
        Returns:
            petri net, initial marking and final marking
           """
    try:

        collection_db = await collection_exists(current_user.username, collection)

        json_obj = []
        async for doc in collection_db.find({}, {"_id": 0}):
            json_obj.append(doc)  # Directly append the document

        print(json_obj)
        # file_content = await file.read()
        # file_extension = os.path.splitext(file.filename)[1]
        #
        # with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        #     temp_file.write(file_content)
        #     temp_file_path = temp_file.name
        #
        # log, net, initial_marking, final_marking, output_path = await alpha_miner_algo(temp_file_path, case_name,separator, )

        # return collection_db['files_hash']

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alpha-miner-algo-quality/")
async def alphaminer_algo_quality(fitness_approach: Quality_Type,
                                  precision_approach: Quality_Type, case_name: str = "client_id",
                                  concept_name: str = "action",
                                  timestamp: str = 'timestamp', separator: str = ";", file: UploadFile = File(...)):
    """
              Applying Alpha Miner algorithm on a log file and saving the model in a png file
            Args:
                separator,timestamp, concept_name,case_name: columns of the csv file
                file: csv or xes log file
            Returns:
                petri net, initial marking and final marking
               """
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        results, zip = await alpha_algo_quality(temp_file_path, case_name, concept_name, timestamp, separator,
                                                fitness_approach.lower(), precision_approach.lower())
        return results, zip
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# able to discover more complex connection, handle loops and connections effectively
@router.post("/alpha-miner-plus/")
async def alpha_plus(case_name: str = "client_id", concept_name: str = "action",
                     timestamp: str = 'timestamp', separator: str = ";", file: UploadFile = File(...)):
    """
               Alpha miner plus :  able to discover more complex connections, handle loops and connections effectively
            Args:
                separator,timestamp, concept_name,case_name: columns of the csv file
                file: csv or xes log file
            Returns:
                petri net, initial marking and final marking
               """
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        log, net, initial_marking, final_marking, output_path = await alpha_miner_plus(temp_file_path, case_name,
                                                                                       concept_name, timestamp,
                                                                                       separator, )
        return FileResponse(output_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alpha-miner-plus-quality/")
async def alpha_miner_plus_qual(fitness_approach: Quality_Type,
                                precision_approach: Quality_Type, case_name: str = "client_id",
                                concept_name: str = "action",
                                timestamp: str = 'timestamp', separator: str = ";",
                                file: UploadFile = File(...)):
    """
            Calculates the quality of the Alpha miner plus model
            Args:
                separator,timestamp, concept_name,case_name: columns of the csv file
                file: csv or xes log file
            Returns:
                petri net, initial marking and final marking
               """
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        results, zip = await alpha_miner_plus_quality(temp_file_path, case_name, concept_name, timestamp, separator,
                                                      fitness_approach.lower(), precision_approach.lower())
        return results, zip
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise e


@router.post("/alpha-miner-frequency/")
async def frequency_alpha_miner(case_name: str = "client_id", concept_name: str = "action",
                                timestamp: str = 'timestamp', separator: str = ";", file: UploadFile = File(...)):
    """
              Creates an Alpha miner petri net with the frequency of the activities and saves it in a png file
            Args:
                separator,timestamp, concept_name,case_name: columns of the csv file
                file: csv or xes log file
            Returns:
                petri net, initial marking and final marking
               """
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        output_path = await freq_alpha_miner(temp_file_path, case_name, concept_name, timestamp, separator)
        return FileResponse(output_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/heuristic_miner/")
async def heuristic_miner_algo(case_name: str = "client_id", concept_name: str = "action",
                               timestamp: str = 'timestamp', separator: str = ";", file: UploadFile = File(...),
                               dependency_threshold: float = Query(0.5, ge=0, le=1),
                               and_threshold: float = Query(0.65, ge=0, le=1),
                               loop_two_threshold: float = Query(0.5, ge=0, le=1)
                               ):
    """
    Applying Alpha Miner algorithm on a log file and saving the model in a png file
        Args:
            separator,timestamp, concept_name,case_name: columns of the csv file
            file: csv or xes log file
            parameter: can be null, so the heuristic net will be created with the default values of the
                parameters, or we chose a parameter (Dependency Threshold, And Threshold, or Loop Two Threshold)
            value: a float value of the parameter,
    Returns: a png file of the heuristic net
               """
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        output_path = await heuristic_miner(temp_file_path, case_name, concept_name, timestamp, separator,
                                            dependency_threshold, and_threshold, loop_two_threshold)
        return FileResponse(output_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/heuristic_petri_net/")
async def heuristic_miner_to_petrinet(fitness_approach: Quality_Type,
                                      precision_approach: Quality_Type, case_name: str = "client_id",
                                      concept_name: str = "action",
                                      timestamp: str = 'timestamp', separator: str = ";",
                                      file: UploadFile = File(...)):
    """
     Generate a petri net from a heuristic net to calculate the quality of the model
        Returns:
            A zip file containing the petri net, pnml file and the quality of the model
    """
    start_time = time.time()
    try:
        file_content = await file.read()
        logger.info(f"File read in {time.time() - start_time:.2f} seconds")

        file_extension = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        logger.info(f"Temp file written in {time.time() - start_time:.2f} seconds")

        results, zip_path = await heuristic_miner_petri(temp_file_path, case_name, concept_name, timestamp, separator,
                                                         fitness_approach.lower(), precision_approach.lower())
        logger.info(f"heuristic_miner_petri executed in {time.time() - start_time:.2f} seconds")
        return results, zip_path
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inductive_miner/")
async def inductive_miner_algo(case_name: str = "client_id", concept_name: str = "action",
                               timestamp: str = 'timestamp', separator: str = ";", file: UploadFile = File(...),
                               noise_threshold: float = Query(0, ge=0, le=1)):
    """
    Args:
        noise_threshold: a float value, filters noisy behavior, activities that are infrequent and outliers
        default value is 0
        separator,timestamp, concept_name,case_name: columns of the csv file
        file: csv or xes log file
        Returns:
            petri net, initial marking and final marking
    """
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        log, net, initial_marking, final_marking, output_path = await inductive_miner(temp_file_path, case_name,
                                                                                      concept_name, timestamp,
                                                                                      separator, noise_threshold)
        return FileResponse(output_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inductive_miner_quality/")
async def inductive_miner_qual(fitness_approach: Quality_Type,
                               precision_approach: Quality_Type, case_name: str = "client_id",
                               concept_name: str = "action",
                               timestamp: str = 'timestamp', separator: str = ";",
                               noise_threshold: float = Query(0, ge=0, le=1),
                               file: UploadFile = File(...)):
    """
        Args:
            file: csv/xes log file
            noise_threshold: a float value, filters noisy behavior, activities that are infrequent and outliers,
                default value is 0
            fitness_approach, precision_approach: chosing if token based or alignement based approach

        Returns:
            zip file: containing a json file of the quality of the model, a png of the petri net and a PNML file

        """
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        print(fitness_approach.lower(), precision_approach.lower())

        results, zip = await inductive_miner_quality(temp_file_path, case_name, concept_name, timestamp, separator,
                                                     noise_threshold, fitness_approach.lower(),
                                                     precision_approach.lower())
        return results, zip
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inductive_process_tree/")
async def inductive_miner_process_tree(case_name: str = "client_id", concept_name: str = "action",
                                       timestamp: str = 'timestamp', separator: str = ";",
                                       file: UploadFile = File(...)):
    """
        Creates and inductive process tree and saves it in a png file
            Args:
                separator,timestamp, concept_name,case_name: columns of the csv file
                file: csv or xes log file
            Returns:
                petri net, initial marking and final marking
               """
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        output_path = await inductive_miner_tree(temp_file_path, case_name, concept_name, timestamp, separator )
        return FileResponse(output_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bpmn_model_inductive/")
async def bpmn_mod(case_name: str = "client_id", concept_name: str = "action",
                   timestamp: str = 'timestamp', separator: str = ";", file: UploadFile = File(...)):
    """
       Creates and inductive BPMN model and saves it in a png file
            Args:
                separator,timestamp, concept_name,case_name: columns of the csv file
                file: csv or xes log file
            Returns:
                BPMN file
               """
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        output_path = await bpmn_model(temp_file_path, case_name, concept_name, timestamp, separator)
        return FileResponse(output_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/directly_follow_graph/")
async def directly_follow_graph(case_name: str = "client_id", concept_name: str = "action",
                                timestamp: str = 'timestamp', separator: str = ";", file: UploadFile = File(...)):
    """
    Generates a graph of the directly follow activities and saves it in a png file
    Args:
        separator,timestamp, concept_name,case_name: columns of the csv file
        file: csv or xes log file
    Returns:
        A tuple with the directly-following activities
    """
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        precision, output_path = await dfg_precision(temp_file_path, case_name, concept_name, timestamp, separator)
        return FileResponse(output_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dfg_to_petrinet/")
async def dfg_to_petrinet_quality(fitness_approach: Quality_Type,
                                  precision_approach: Quality_Type, case_name: str = "client_id",
                                  concept_name: str = "action",
                                  timestamp: str = 'timestamp', separator: str = ";",
                                  file: UploadFile = File(...)):
    """
     Converts the dfg to a petri net to calculate the quality of the resulting model
    Returns:
        zip file: containing a json file of the quality of the model, a png of the petri net and a PNML file
     Returns : the precision of the Directly Follow Graph
               """
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        print(fitness_approach.lower(), precision_approach.lower())

        results, zip = await dfg_petri_quality(temp_file_path, case_name, concept_name, timestamp, separator,
                                               fitness_approach.lower(), precision_approach.lower())
        return results, zip
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dfg_performance/")
async def dfg_perf(case_name: str = "client_id", concept_name: str = "action",
                   timestamp: str = 'timestamp', separator: str = ";", file: UploadFile = File(...)):
    """
     Discovers a performance directly-follows graph from an event log and saves it in a png file
   Args:
    separator,timestamp, concept_name,case_name: columns of the csv file,
    file: csv or xes log file
    Returns:
        petri net, initial marking and final marking
               """
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        output_path = await dfg_performance(temp_file_path, case_name, concept_name, timestamp, separator)
        return FileResponse(output_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/animate_process/")
async def process_animation(file: UploadFile = File(...)):
    try:
        # Save the uploaded file
        file_path = os.path.join("src/temp", file.filename)
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        html_file_path = await process_animate(file_path)
        print("file path ", html_file_path)
        list_files = []
        list_files.append(html_file_path)
        list_files.append("src/temp/process_animation_files")
        zip_file_path = create_zip_file(list_files)

        return FileResponse(zip_file_path, media_type="application/zip", filename="animation.zip")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
