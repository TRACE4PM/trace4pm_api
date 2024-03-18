from pm4py.objects.conversion.log import converter as log_converter
import tempfile
from tempfile import NamedTemporaryFile
import pandas as pd
import subprocess
import io
import pm4py
import os
import glob
import json
from zipfile import ZipFile
from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator


async def read_csv(file_content, sep):
    dataframe = pd.read_csv(io.StringIO(file_content.decode('utf-8')), sep=sep)

    #renaming the col ending with _id
    dataframe.rename(columns=lambda x: 'case:concept:name' if x.endswith('_id') else x, inplace=True)
    dataframe.rename(columns=lambda x: 'time:timestamp' if x.endswith('timestamp') else x, inplace=True)
    dataframe.rename(columns={'action': 'concept:name'}, inplace=True)

    # Convert timestamp column to datetime and handle mixed format
    dataframe['time:timestamp'] = pd.to_datetime(dataframe['time:timestamp'], format='mixed')

    dataframe = pm4py.format_dataframe(dataframe, case_id='case:concept:name', activity_key='concept:name',
                                       timestamp_key='time:timestamp')
    log = pm4py.convert_to_event_log(dataframe)

    return log


async def read_files(file, sep):
    file_content = await file.read()
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name
        if file.filename.endswith('.csv'):
            log = await read_csv(file_content,sep)
        elif file.filename.endswith('.xes'):
            log = pm4py.read_xes(temp_file_path)

    os.remove(temp_file_path)
    return log




async def rename_columns(dataframe, case_id, action, timestamp):

    dataframe.rename(columns={timestamp: 'time:timestamp'}, inplace=True)
    dataframe.rename(columns={action: 'concept:name'}, inplace=True)
    dataframe.rename(columns={case_id: 'case:concept:name'}, inplace=True)

    return dataframe


def latest_image():
    tmp_dir = os.path.expanduser('/tmp')
    list_of_files = glob.glob(os.path.join(tmp_dir, '*'))
    latest_image = max(list_of_files, key=os.path.getctime)

    return latest_image


def generate_zip(diagram_path, pnml_path, qual_path):
    zip_path = "src/outputs/Zipped_file.zip"
    with ZipFile(zip_path, 'w') as zip_object:
        # Adding files that need to be zipped
        zip_object.write(pnml_path,
                         arcname='pnml_file')
        zip_object.write(diagram_path, arcname="gviz_diagram")
        zip_object.write(qual_path, arcname="algo_quality")

    # Check to see if the zip file is created
    if os.path.exists(zip_path):
        return "ZIP file created :", zip_path
    else:
        return "ZIP file not created"


def calculate_quality(log, net, im, fm, f, p):
    gen = generalization_evaluator.apply(log, net, im, fm)
    # TODO : add fitness aligne..
    if f == 1:
        fitness = pm4py.fitness_token_based_replay(log, net, im, fm)
    else:
        fitness = pm4py.fitness_alignments(log, net, im, fm)
        print("fit align")
    if p == 1:
        prec = pm4py.precision_token_based_replay(log, net, im, fm)
    else:
        prec = pm4py.precision_alignments(log, net, im, fm)
        print("fit align")

    simp = simplicity_evaluator.apply(net)

    results = {"Fitness": fitness,
               "Precision": prec,
               "Generalization": gen,
               "Simplicity": simp}

    json_path = "src/outputs/quality.json"
    with open(json_path, "w") as outfile:
        json.dump(results, outfile)

    return json_path
