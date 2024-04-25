import os
import io
import glob
import pandas as pd
import tempfile
import pm4py
import json


async def read_csv(file):
    # file_content = await file.read()
    dataframe = pd.read_csv(file, sep=";")

    # renaming the col ending with _id
    dataframe.rename(columns=lambda x: 'case:concept:name' if x.endswith('_id') else x, inplace=True)
    dataframe.rename(columns=lambda x: 'time:timestamp' if x.endswith('timestamp') else x, inplace=True)
    dataframe.rename(columns={'action': 'concept:name'}, inplace=True)

    # Convert timestamp column to datetime and handle mixed format
    dataframe['time:timestamp'] = pd.to_datetime(dataframe['time:timestamp'], format='mixed')

    dataframe = pm4py.format_dataframe(dataframe, case_id='case:concept:name', activity_key='concept:name',
                                       timestamp_key='time:timestamp')
    log = pm4py.convert_to_event_log(dataframe)

    return log


async def read_files(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    if extension == '.csv':
        log = await read_csv(file_path)
        return log
    elif extension == '.xes':
        log = pm4py.read_xes(file_path)
        return log


def latest_image():
    tmp_dir = os.path.expanduser('/tmp')
    list_of_files = glob.glob(os.path.join(tmp_dir, '*'))
    latest_image = max(list_of_files, key=os.path.getctime)

    return latest_image
