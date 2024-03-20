import os
from fastapi import FastAPI, UploadFile, File, APIRouter, HTTPException, Query, Request, Depends
from fastapi.responses import JSONResponse, Response
from discover.main import (alpha_miner_algo, alpha_algo_quality, alpha_miner_plus, alpha_miner_plus_quality,
                           freq_alpha_miner, heuristic_miner, heuristic_miner_petri, heuristic_params_threshold,
                           inductive_miner, inductive_miner_quality, directly_follow,
                           dfg_petri_quality, inductive_miner_tree,
                           dfg_performance, bpmn_model, process_animate)

router = APIRouter(
    prefix="/discovery",
    tags=["discovery"]
)


@router.post("/alpha-miner/")
async def alpha_miner_algorithm(file: UploadFile = File(...)):
    try:
        await alpha_miner_algo(file)
        return {"message": "png file saved"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alpha-miner-algo-quality/")
async def alphaminer_algo_quality(file: UploadFile = File(...), fitness_approach: str = "token based",
                                  precision_approach: str = "token based"):
    try:
        zip = await alpha_algo_quality(file, fitness_approach, precision_approach)
        return zip
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# able to discover more complex connection, handle loops and connections effectively
@router.post("/alpha-miner-plus/")
async def alpha_plus(file: UploadFile = File(...)):
    try:
        await alpha_miner_plus(file)

        # headers = {"message": "png file saved"}
        # return FileResponse(latest_image(), headers=headers)
        return {"message": "png file saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alpha-miner-plus-quality/")
async def alpha_miner_plus_quality(file: UploadFile = File(...), fitness_approach: str = "token based",
                                   precision_approach: str = "token based"):
    try:
        zip = await alpha_miner_plus_quality(file, fitness_approach, precision_approach)
        return zip
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alpha-miner-frequency/")
async def frequency_alpha_miner(file: UploadFile = File(...)):
    try:
        await freq_alpha_miner(file)
        return {"message": "png file saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/heuristic_miner/")
async def heuristic_miner_algo(file: UploadFile = File(...)):
    try:
        await heuristic_miner(file)
        return {"message": "png file saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/heuristic_petri_net/")
async def heuristic_miner_to_petrinet(file: UploadFile = File(...), fitness_approach: str = "token based",
                                      precision_approach: str = "token based"):
    try:
        zip = await heuristic_miner_petri(file, fitness_approach, precision_approach)
        return zip
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/heuristic_miner_params/")
async def heuristic_params(file: UploadFile = File(...), parameter: str = Query("dependency threshold"),
                           value: float = Query(0.5, ge=0, le=1)):
    try:
        await heuristic_params_threshold(file, parameter, value)
        return {"message": "png file saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inductive_miner/")
async def inductive_miner_algo(file: UploadFile = File(...),
                               noise_threshold: float = Query(0, ge=0, le=1)):
    try:
        await inductive_miner(file, noise_threshold)
        return {"message": "petri net saved in png file"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inductive_miner_quality/")
async def inductive_miner_qual(file: UploadFile = File(...),
                               noise_threshold: float = Query(0, ge=0, le=1), fitness_approach: str = "token based",
                               precision_approach: str = "token based"):
    try:
        zip = await inductive_miner_quality(file, noise_threshold, fitness_approach, precision_approach)
        return zip
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inductive_process_tree/")
async def inductive_miner_process_tree(file: UploadFile = File(...)):
    try:
        await inductive_miner_tree(file)
        return {"message": "Process tree saved in file"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/directly_follow_graph/")
async def directly_follow_grap(file: UploadFile = File(...)):
    try:
        result = await directly_follow(file)
        return {"message": "png file saved","precision": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dfg_to_petrinet/")
async def dfg_to_petrinet_quality(file: UploadFile = File(...), fitness_approach: str = "token based",
                          precision_approach: str = "token based"):
    try:
        zip = await dfg_petri_quality(file, fitness_approach, precision_approach)
        return zip
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dfg_performance/")
async def dfg_perf(file: UploadFile = File(...)):
    try:
        await dfg_performance(file)
        return {"message": "png file saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bpmn_model_inductive/")
async def bpmn_mod(file: UploadFile = File(...)):
    try:
        await bpmn_model(file)
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
