from datetime import datetime

from pydantic import BaseModel


class FileCreate(BaseModel):
    filename: str

    class Config:
        orm_mode = True


class FileRead(FileCreate):
    id: int
    create_date: datetime
    user_id: int
