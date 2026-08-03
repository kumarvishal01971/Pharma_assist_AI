from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str = ""
    database_url: str = "mysql+pymysql://root:root@localhost:3306/aivoa_complaints"
    extraction_model: str = "gemma2-9b-it"
    reasoning_model: str = "llama-3.3-70b-versatile"
    cors_allowed_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,http://0.0.0.0:5173,"
        "http://10.0.10.47:5173,http://10.0.2.15:5173,"
        "https://pharma-assist-ai-ten.vercel.app"
    )
    cors_allowed_origin_regex: str = r"https://.*\.(app\.github\.dev|vercel\.app)"

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        env_file_encoding="utf-8",
    )


settings = Settings()


def parse_cors_origins(raw_value: str | None) -> list[str]:
    if not raw_value:
        return []
    return [item.strip() for item in raw_value.split(",") if item.strip()]
