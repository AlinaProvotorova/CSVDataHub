import os
from pathlib import Path

import pandas as pd
from fastapi import HTTPException

from app.api.validators import FILE_NOT_FOUND_MESSAGE
from app.core.config import settings

if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR)


async def filter_and_sort_csv(filename, filters=None, sort_by=None):
    upload_folder = Path(settings.UPLOAD_DIR)
    file_path = upload_folder / filename
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=FILE_NOT_FOUND_MESSAGE.format(filename))
    if filters is not None:
        for column, condition in filters.items():
            df = df[df[column] == condition]

    if sort_by is not None:
        df = df.sort_values(by=sort_by)

    records = df.to_dict(orient='records')

    return records
