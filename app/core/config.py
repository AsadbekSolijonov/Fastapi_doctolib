from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    SECRET_KEY: str
    REFRESH_TOKEN_EXPIRE_DAYS: int
    REFRESH_COOKIE_NAME: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
