import os

from fastapi import HTTPException

from app.core.user import User
from app.models import File

INVALID_JSON_FORMAT_MESSAGE = "Некорректный формат JSON для фильтров"
INVALID_FILE_EXTENSION_MESSAGE = "Разрешены только файлы с расширением .csv"
FORBIDDEN_MESSAGE = "Forbidden"
DUPLICATE_FILENAME_MESSAGE = "Файл с именем {} уже был загружен"
FILE_NOT_FOUND_MESSAGE = "Файл {} не найден"


async def check_upload_file(file: File, file_path: str):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail=INVALID_FILE_EXTENSION_MESSAGE)

    if os.path.exists(file_path):
        raise HTTPException(status_code=400, detail=DUPLICATE_FILENAME_MESSAGE.format(file.filename))


async def check_file_access_and_existence(file: File, user: User, file_name: str):
    if not file or file is None:
        raise HTTPException(status_code=404, detail=FILE_NOT_FOUND_MESSAGE.format(file_name))
    if not user.is_superuser and file.user_id != user.id:
        raise HTTPException(status_code=403, detail=FORBIDDEN_MESSAGE)

