from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str = ""
    database_url: str = "mysql+pymysql://root:root@localhost:3306/aivoa_complaints"
    extraction_model: str = "gemma2-9b-it"
    reasoning_model: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        env_file_encoding="utf-8",
    )


settings = Settings()
