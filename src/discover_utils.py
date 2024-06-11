import os
import io
import glob
import pandas as pd
import tempfile
import pm4py
import json


async def read_csv(file):
    dataframe = pd.read_csv(file, sep=";")

    # renaming the col ending with _id
    dataframe.rename(columns=lambda x: 'case:concept:name' if x.endswith('_id') else x, inplace=True)
    dataframe.rename(columns=lambda x: 'time:timestamp' if x.endswith('timestamp') else x, inplace=True)
    dataframe.rename(columns={'action': 'concept:name'}, inplace=True)

    # Convert timestamp column to datetime and handle mixed format
    dataframe['time:timestamp'] = pd.to_datetime(dataframe['time:timestamp'], format='mixed')

    return dataframe


async def read_files(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    if extension == '.csv':
        dataframe = await read_csv(file_path)
        return dataframe
    elif extension == '.xes':
        log = pm4py.read_xes(file_path)
        return log


def latest_image():
    tmp_dir = os.path.expanduser('/tmp')
    list_of_files = glob.glob(os.path.join(tmp_dir, '*'))
    latest_image = max(list_of_files, key=os.path.getctime)

    return latest_image
