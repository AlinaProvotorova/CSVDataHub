import os
from pathlib import Path

import pandas as pd
from fastapi import HTTPException

UPLOAD_DIR = "data"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


async def filter_and_sort_csv(filename, filters=None, sort_by=None):
    upload_folder = Path(UPLOAD_DIR)
    file_path = upload_folder / filename
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Файл '{filename}' не найден")
    if filters is not None:
        for column, condition in filters.items():
            print(column)
            df = df[df[column] == condition]

    if sort_by is not None:
        df = df.sort_values(by=sort_by)

    records = df.to_dict(orient='records')

    return records
