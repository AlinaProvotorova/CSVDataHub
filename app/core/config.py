from typing import Optional

from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str = 'My Api'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'SECRET'
    superuser_email: Optional[EmailStr] = 'None'
    superuser_password: Optional[str] = None

    class Config:
        env_file = '.env'


settings = Settings()
