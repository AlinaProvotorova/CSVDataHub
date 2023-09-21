import json
import shutil
from typing import List

from fastapi import APIRouter
from fastapi import Depends, Query, HTTPException
from fastapi import File
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_upload_file, check_file_access_and_existence, INVALID_JSON_FORMAT_MESSAGE
from app.core.config import settings
from app.core.db import get_async_session
from app.core.user import User
from app.core.user import current_user, current_superuser
from app.crud.file import file_crud
from app.schemas.file import FileCreate, FileRead
from app.services.file_service import filter_and_sort_csv

router = APIRouter()


@router.get(
    "/files/",
    dependencies=[Depends(current_superuser)],
    response_model=list[FileRead],
    tags=["admin"]
)
async def list_files(
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперпользователей.
    Получение списка всех файлов с информацией о колонках.
    """
    files = await file_crud.get_multi(session)
    return files


@router.get(
    "/my/files/",
    dependencies=[Depends(current_user)],
    response_model=list[FileRead],
    tags=["user", "admin"]
)
async def list_files(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
) -> List[FileRead]:
    """
    Только для авторизованных пользователей.
    Получение списка файлов которые загрузил пользователь с информацией о колонках.
    """
    files = await file_crud.get_multi(session, user=user)
    return files


@router.get(
    "/data/{file_name}/",
    dependencies=[Depends(current_user)],
    tags=["user", "admin"]
)
async def get_data(
        file_name: str,
        session: AsyncSession = Depends(get_async_session),
        filters: str = Query(None, description="Столбец и значение для фильтрации"),
        sort_by: str = Query(None, description="Имя столбца для сортировки"),
        user: User = Depends(current_user)
):
    """
    Только для суперпользователей.
    Получение данных из конкретного файла с опциональными фильтрацией и сортировкой по одному или нескольким столбцам
    """
    file = await file_crud.get_by_filename(file_name, session)
    await check_file_access_and_existence(file, user, file_name)
    try:
        filters = json.loads(filters) if filters else None
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=INVALID_JSON_FORMAT_MESSAGE)
    return await filter_and_sort_csv(file.filename, filters, sort_by)


@router.post(
    "/upload/",
    dependencies=[Depends(current_user)],
    tags=["user", "admin"]
)
async def upload_file(
        file: UploadFile = File(...),
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
):
    """
    Только для авторизованных пользователей.
    Загрузка файла на сервер.
    """
    file_path = settings.UPLOAD_FOLDER / file.filename
    await check_upload_file(file, file_path)
    with open(file_path, "wb") as file_object:
        shutil.copyfileobj(file.file, file_object)
    db_file = FileCreate(filename=file.filename)
    await file_crud.create(db_file, session, user)
    return {"detail": "Файл успешно загружен"}


@router.delete(
    "/delete/{file_id}/",
    dependencies=[Depends(current_user)],
    tags=["admin", "user"]
)
async def delete_file(
        file_id: int,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
):
    """
    Только для авторизованных пользователей.
    Удаление файла по его Id
    """
    file = await file_crud.get(file_id, session)
    await check_file_access_and_existence(file, user, file.filename)
    await file_crud.remove(file, session)
    file_path = settings.UPLOAD_FOLDER / file.filename
    if file_path.exists():
        file_path.unlink()

    return {"detail": "Файл успешно удален"}
