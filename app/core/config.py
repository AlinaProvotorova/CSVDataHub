from pathlib import Path
from typing import Optional

from pydantic import EmailStr, BaseSettings


class Settings(BaseSettings):
    app_title: str = 'CSVDataHub'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'SECRET'
    superuser_email: Optional[EmailStr] = 'admin@ru.com'
    superuser_password: Optional[str] = None

    UPLOAD_DIR = "data"
    UPLOAD_FOLDER = Path(UPLOAD_DIR)

    class Config:
        env_file = '.env'


settings = Settings()
