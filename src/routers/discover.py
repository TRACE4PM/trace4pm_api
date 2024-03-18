import os
from fastapi import FastAPI, UploadFile, File, APIRouter, HTTPException, Query, Request, Depends
from fastapi.responses import JSONResponse, Response
from starlette.responses import FileResponse
import pm4py
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.alpha import variants
from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator
from pm4py.objects.conversion.dfg.variants import to_petri_net_invisibles_no_duplicates
from pm4py.visualization.align_table import visualizer as diagram_visual
from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from pm4py.visualization.dfg import visualizer as dfg_visualizer
from ..models.params import MiningResult
from ..discover_utils import read_files, read_csv, latest_image, generate_zip, calculate_quality
import tempfile
import subprocess
from discover.main import (alpha_miner_alg, alpha_miner_plus, freq_alpha_miner, heuristic_miner,
                           heuristic_params_threshold, inductive_miner, dfg_to_petrinet, inductive_miner_tree,
                           bpmn_model, dfg_perfor, heuristic_miner_petri, directly_follow,process_animate)
from ..stats_utils import create_csv_file

router = APIRouter(
    prefix="/discovery",
    tags=["discovery"]
)


@router.post("/alpha-miner/")
async def alpha_miner_algorithm(file: UploadFile = File(...), sep: str = ';'):
    try:

        log, net, im, fm = await alpha_miner_alg(file, sep)

        gviz = pn_visualizer.apply(net, im, fm)
        # pn_visualizer.view(gviz)
        diagram_visual.save(gviz, "src/outputs/diagram.png")

        headers = {"message": "png file saved"}
        return FileResponse(latest_image(), headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alpha-miner-algo-quality/")
async def alpha_algo_quality(file: UploadFile = File(...), sep: str = ';', fitness_approach: int = 1,
                             precision_appreach: int = 1):
    try:
        log, net, im, fm = await alpha_miner_alg(file, sep)
        gviz = pn_visualizer.apply(net, im, fm)
        # pn_visualizer.view(gviz)
        diagram_visual.save(gviz, "src/outputs/diagram.png")

        json_path = calculate_quality(log, net, im, fm, fitness_approach, precision_appreach)
        pm4py.write.write_pnml(net, im, fm, "src/outputs/pnml_file")

        zip = generate_zip("src/outputs/diagram.png", "src/outputs/pnml_file.pnml", json_path)

        return zip

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# able to discover more complex connection, handle loops and connections effectively
@router.post("/alpha-miner-plus/")
async def alpha_plus(file: UploadFile = File(...), sep: str = ';'):
    try:
        log, net, im, fm = await alpha_miner_plus(file, sep)
        gviz = pn_visualizer.apply(net, im, fm)
        # pn_visualizer.view(gviz)
        diagram_visual.save(gviz, "src/outputs/diagram.png")
        headers = {"message": "png file saved"}
        return FileResponse(latest_image(), headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alpha-miner-plus-quality/")
async def alpha_miner_plus_quality(file: UploadFile = File(...), sep: str = ';', fitness_approach: int = 1,
                                   precision_appreach: int = 1):
    try:
        log, net, im, fm = await alpha_miner_plus(file, sep)
        gviz = pn_visualizer.apply(net, im, fm)
        # pn_visualizer.view(gviz)
        diagram_visual.save(gviz, "src/outputs/diagram.png")

        json_path = calculate_quality(log, net, im, fm, fitness_approach, precision_appreach)
        pm4py.write.write_pnml(net, im, fm, "src/outputs/pnml_file")

        zip = generate_zip("src/outputs/diagram.png", "src/outputs/pnml_file.pnml", json_path)

        return zip
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alpha-miner-frequency/")
async def frequency_alpha_miner(file: UploadFile = File(...), sep: str = ';'):
    try:
        gviz = await freq_alpha_miner(file, sep)
        # pn_visualizer.view(gviz)
        diagram_visual.save(gviz, "src/outputs/diagram.png")
        headers = {"message": "png file saved"}
        return FileResponse(latest_image(), headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/heuristic_miner/")
async def heuristic_miner_algo(file: UploadFile = File(...), sep: str = ';'):
    try:
        heuristic_net = await heuristic_miner(file, sep)
        # pm4py.view_heuristics_net(heuristic_net)
        gviz = hn_visualizer.apply(heuristic_net)
        hn_visualizer.save(gviz, "src/outputs/diagram.png")

        headers = {"message": "png file saved"}
        return FileResponse(latest_image(), headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/heuristic_petri_net/")
async def heuristic_miner_to_petrinet(file: UploadFile = File(...), sep: str = ';'):
    try:
        net, im, fm = await heuristic_miner_petri(file, sep)
        gviz = pn_visualizer.apply(net, im, fm)
        # pn_visualizer.view(gviz)
        diagram_visual.save(gviz, "src/outputs/diagram.png")

        headers = {"message": "png file saved"}
        return FileResponse(latest_image(), headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/heuristic_miner_params/")
async def heuristic_params(file: UploadFile = File(...), sep: str = ';',
                           value: float = Query(0.5, ge=0, le=1)):
    try:
        heu_net = await heuristic_params_threshold(file, sep, value)
        gviz = hn_visualizer.apply(heu_net)
        hn_visualizer.save(gviz, "src/outputs/diagram.png")

        headers = {"message": "png file saved"}
        return FileResponse(latest_image(), headers=headers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inductive_miner/")
async def inductive_miner_algo(file: UploadFile = File(...), sep: str = ';',
                               noise_threshold: float = Query(0, ge=0, le=1)):
    try:
        log, net, initial_marking, final_marking = await inductive_miner(file, sep, noise_threshold)
        gviz = pn_visualizer.apply(net, initial_marking, final_marking)
        diagram_visual.save(gviz, "src/outputs/diagram.png")

        headers = {"message": "petri net saved in png file"}
        return FileResponse(latest_image(), headers=headers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inductive_miner_quality/")
async def inductive_miner_qual(file: UploadFile = File(...), sep: str = ';',
                               noise_threshold: float = Query(0, ge=0, le=1), fitness_approach: int = 1,
                               precision_appreach: int = 1):
    try:
        log, net, initial_marking, final_marking = await inductive_miner(file, sep, noise_threshold)
        gviz = pn_visualizer.apply(net, initial_marking, final_marking)
        diagram_visual.save(gviz, "src/outputs/diagram.png")

        json_path = calculate_quality(log, net, initial_marking, final_marking, fitness_approach, precision_appreach)
        pm4py.write.write_pnml(net, initial_marking, final_marking, "src/outputs/pnml_file")

        zip = generate_zip("src/outputs/diagram.png", "src/outputs/pnml_file.pnml", json_path)

        return zip

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inductive_process_tree/")
async def inductive_miner_process_tree(file: UploadFile = File(...), sep: str = ';'):
    try:

        tree = await inductive_miner_tree(file, sep)
        # pm4py.view_process_tree(tree)
        gviz = pt_visualizer.apply(tree)
        pt_visualizer.save(gviz, "src/outputs/diagram.png")

        headers = {"message": "Process tree saved in file"}
        return FileResponse(latest_image(), headers=headers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/directly_follow_graph/")
async def directly_follow_grap(file: UploadFile = File(...), sep: str = ';'):
    try:
        dfg, start_activities, end_activities = await directly_follow(file, sep)
        # dfg, start_activities, end_activities = result

        # pm4py.view_dfg(dfg, start_activities, end_activities)
        # pm4py.save_vis_dfg(dfg, start_activities, end_activities, "src/outputs/diagram.png")

        # gviz = pm4py.view_dfg(dfg, start_activities, end_activities)
        # pn_visualizer.save(gviz, "src/outputs/diagram.png")
        # precision = pm4py.algo.evaluation.precision.dfg.algorithm.apply(log, dfg, start_activities, end_activities)
        # results = {"precision": str(precision)}
        return dfg, start_activities, end_activities

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dfg_to_petrinet/")
async def directly_follow(file: UploadFile = File(...), sep: str = ';'):
    try:

        # return the log file to calculate the quality

        # log = await read_files(file, sep)
        net, initial_marking, final_marking = await dfg_to_petrinet(file, sep)
        gviz = pn_visualizer.apply(net, initial_marking, final_marking)
        diagram_visual.save(gviz, "src/outputs/diagram.png")


        # json_path = calculate_quality(log, net, initial_marking, final_marking, fitness_approach, precision_appreach)
        # pm4py.write.write_pnml(net, initial_marking, final_marking, "src/outputs/pnml_file")
        #
        # zip = generate_zip("src/outputs/diagram.png", "src/outputs/pnml_file.pnml", json_path)
        #
        # return zip

        headers = {"message": "petri net saved in png file"}
        return FileResponse(latest_image(), headers=headers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dfg_performance/")
async def dfg_perf(file: UploadFile = File(...), sep: str = ';'):
    try:
        performance_dfg, start_activities, end_activities = await dfg_perfor(file, sep)
        # pm4py.view_performance_dfg(performance_dfg, start_activities, end_activities)
        pm4py.save_vis_performance_dfg(performance_dfg, start_activities, end_activities, "src/outputs/dfg.png")
        # pm4py.save_vis_performance_dfg(performance_dfg, start_activities, end_activities, 'perf_dfg.png')
        headers = {"message": "dfg saved in png file"}
        return FileResponse(latest_image(), headers=headers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bpmn_model_inductive/")
async def bpmn_mod(file: UploadFile = File(...), sep: str = ';'):
    try:
        bpmn = await bpmn_model(file, sep)
        pm4py.visualization.bpmn.visualizer.save(bpmn, "src/outputs/diagram.png")
        pm4py.view_bpmn(bpmn)
        return FileResponse(latest_image())

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
