import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str = os.environ.get("GROQ_API_KEY", "")
    host: str = os.environ.get("HOST", "0.0.0.0")
    port: int = int(os.environ.get("PORT", "8000"))
    primary_model: str = "llama-3.3-70b-versatile"
    fallback_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
