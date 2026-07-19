from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # DB 접속 정보 (로컬 개발 기본값)
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "wh"
    db_user: str = "seoyoon"
    db_password: str = ""

    # GPT api
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    # .env에서 읽어오기
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
