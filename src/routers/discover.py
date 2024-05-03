import os
from fastapi import FastAPI, UploadFile, File, APIRouter, HTTPException, Query, Request, Depends
from fastapi.responses import JSONResponse, Response
from discover.main import (alpha_miner_algo, alpha_algo_quality, alpha_miner_plus, alpha_miner_plus_quality,
                           freq_alpha_miner, heuristic_miner, heuristic_miner_petri,
                           inductive_miner, inductive_miner_quality, inductive_miner_tree,
                           dfg_precision,dfg_petri_quality,
                           dfg_performance, bpmn_model, process_animate)
from ..models.params import Quality_Type
import tempfile
import io

router = APIRouter(
    prefix="/discovery",
    tags=["discovery"]
)


@router.post("/alpha-miner/")
async def alpha_miner_algorithm(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        await alpha_miner_algo(temp_file_path)
        return {"message": "png file saved"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alpha-miner-algo-quality/")
async def alphaminer_algo_quality(fitness_approach: Quality_Type,
                                  precision_approach: Quality_Type, file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        zip = await alpha_algo_quality(temp_file_path, fitness_approach.lower(), precision_approach.lower())
        return zip
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# able to discover more complex connection, handle loops and connections effectively
@router.post("/alpha-miner-plus/")
async def alpha_plus(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        await alpha_miner_plus(temp_file_path)

        return {"message": "png file saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alpha-miner-plus-quality/")
async def alpha_miner_plus_quality(fitness_approach: Quality_Type,
                                  precision_approach: Quality_Type, file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        zip = await alpha_miner_plus_quality(temp_file_path, fitness_approach.lower(), precision_approach.lower())
        return zip
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alpha-miner-frequency/")
async def frequency_alpha_miner(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        await freq_alpha_miner(temp_file_path)
        return {"message": "png file saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/heuristic_miner/")
async def heuristic_miner_algo(file: UploadFile = File(...),
                               dependency_threshold: float = Query(0.5, ge=0, le=1),
                               and_threshold: float = Query(0.65, ge=0, le=1),
                               loop_two_threshold: float = Query(0.5, ge=0, le=1)
                               ):
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        await heuristic_miner(temp_file_path, dependency_threshold, and_threshold, loop_two_threshold)
        return {"message": "png file saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/heuristic_petri_net/")
async def heuristic_miner_to_petrinet(fitness_approach: Quality_Type,
                                  precision_approach: Quality_Type, file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        zip = await heuristic_miner_petri(temp_file_path, fitness_approach.lower(), precision_approach.lower())
        return zip
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inductive_miner/")
async def inductive_miner_algo(file: UploadFile = File(...),
                               noise_threshold: float = Query(0, ge=0, le=1)):
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        await inductive_miner(temp_file_path, noise_threshold)
        return {"message": "petri net saved in png file"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inductive_miner_quality/")
async def inductive_miner_qual(fitness_approach: Quality_Type,
                               precision_approach: Quality_Type, noise_threshold: float = Query(0, ge=0, le=1),
                               file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        zip = await inductive_miner_quality(temp_file_path, noise_threshold, fitness_approach.lower(), precision_approach.lower())
        return zip
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inductive_process_tree/")
async def inductive_miner_process_tree(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        await inductive_miner_tree(temp_file_path)
        return {"message": "Process tree saved in file"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bpmn_model_inductive/")
async def bpmn_mod(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        await bpmn_model(temp_file_path)
        return {"message": "png file saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/directly_follow_graph/")
async def directly_follow_graph(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        result = await dfg_precision(temp_file_path)
        return {"message": "png file saved", "precision": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dfg_to_petrinet/")
async def dfg_to_petrinet_quality(fitness_approach: Quality_Type,
                               precision_approach: Quality_Type, noise_threshold: float = Query(0, ge=0, le=1),
                               file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        zip = await dfg_petri_quality(temp_file_path, fitness_approach.lower(), precision_approach.lower())
        return zip
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dfg_performance/")
async def dfg_perf(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        await dfg_performance(temp_file_path)
        return {"message": "png file saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/animate_process/")
async def process_animation(file: UploadFile = File(...)):
    try:
        # Save the uploaded file
        file_path = os.path.join("src/logs", file.filename)
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        res = await process_animate(file_path)
        if res != 0:
            raise HTTPException(status_code=500, detail="R script execution failed.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

