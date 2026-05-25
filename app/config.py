from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str = ""
    host: str = "0.0.0.0"
    port: int = 8000
    primary_model: str = "openai/gpt-oss-120b"
    fallback_model: str = "openai/gpt-oss-20b"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
