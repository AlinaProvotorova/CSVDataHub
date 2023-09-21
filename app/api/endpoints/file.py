import json
import shutil

from fastapi import APIRouter
from fastapi import Depends, Query, HTTPException
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UPLOAD_FOLDER
from app.core.db import get_async_session
from app.core.user import User
from app.core.user import current_user
from app.crud.file import file_crud
from app.models.file import File
from app.services.file_service import filter_and_sort_csv
from app.schemas.file import FileBase
router = APIRouter()


@router.get(
    "/files/",
    dependencies=[Depends(current_user)],
    response_model=list[FileBase],
)
async def list_files(
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для авторизованных пользователей.
    Получение списка файлов с информацией о колонках.
    """
    files = await file_crud.get_multi(session)
    return files.scalars().all()


@router.get(
    "/data/{file_name}/",
    dependencies=[Depends(current_user)],
)
async def get_data(
        file_name: str,
        session: AsyncSession = Depends(get_async_session),
        filters: str = Query(None, description="Столбец и значение для фильтрации"),
        sort_by: str = Query(None, description="Имя столбца для сортировки"),

):
    """
    Только для авторизованных пользователей.
    Получение данных из конкретного файла с опциональными фильтрацией и сортировкой по одному или нескольким столбцам
    """
    file = await file_crud.get_by_filename(file_name, session)
    if not file:
        raise HTTPException(status_code=404, detail=f"Файл '{file_name}' не найден")
    try:
        filters = json.loads(filters) if filters else None
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail="Некорректный формат JSON для фильтров")
    return await filter_and_sort_csv(file.filename, filters, sort_by)


@router.post(
    "/upload/",
    dependencies=[Depends(current_user)],
)
async def upload_file(
        file: UploadFile = UploadFile(...),
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
):
    """
    Только для авторизованных пользователей.
    Загрузка файла на сервер.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Разрешены только файлы с расширением .csv")

    file_path = UPLOAD_FOLDER / file.filename
    with open(file_path, "wb") as file_object:
        shutil.copyfileobj(file.file, file_object)

    db_file = FileBase(filename=file.filename)
    file_crud.create(db_file, session, user)
    # session.add(db_file)
    # await session.commit()
    return {"detail": "Файл успешно загружен"}
