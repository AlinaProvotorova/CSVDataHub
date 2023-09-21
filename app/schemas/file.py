from datetime import datetime

from pydantic import BaseModel


class FileBase(BaseModel):
    filename: str

    class Config:
        orm_mode = True
