from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import model_validator


class Settings(BaseSettings):

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DATABASE_URL: Optional[str] = None

    @model_validator(mode="after")
    def get_database_url(cls, values):
        values.DATABASE_URL = f"postgresql+asyncpg://{values.DB_USER}:{values.DB_PASS}@{values.DB_HOST}:{values.DB_PORT}/{values.DB_NAME}"
        return values

    class Config:
        env_file = '.env'

settings = Settings()