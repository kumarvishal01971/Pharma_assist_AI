from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str = ""
    database_url: str = "mysql+pymysql://root:root@localhost:3306/aivoa_complaints"
    extraction_model: str = "gemma2-9b-it"
    reasoning_model: str = "llama-3.3-70b-versatile"

    class Config:
        env_file = ".env"


settings = Settings()
