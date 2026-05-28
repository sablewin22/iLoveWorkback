import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str = os.environ.get("GROQ_API_KEY", "")
    host: str = os.environ.get("HOST", "0.0.0.0")
    port: int = int(os.environ.get("PORT", "8000"))
    primary_model: str = "openai/gpt-oss-120b"
    fallback_model: str = "openai/gpt-oss-20b"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
