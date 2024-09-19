import os
import io
import glob
import zipfile
from typing import List

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

def create_zip_file(file_paths: List[str]) -> str:
    """Create a zip file containing the provided files and directories."""
    temp_dir = tempfile.mkdtemp()
    zip_file_path = os.path.join(temp_dir, "clusters.zip")

    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in file_paths:
            if os.path.isdir(file_path):
                for root, _, files in os.walk(file_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        arcname = os.path.join("process_animation_files", os.path.relpath(full_path, start=file_path))
                        zip_file.write(full_path, arcname)
            else:
                zip_file.write(file_path, os.path.basename(file_path))
    return zip_file_path