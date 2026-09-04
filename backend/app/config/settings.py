from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Workbench"
    MAX_UPLOAD_SIZE_MB: int = 25
    DATABASE_URL: str = "sqlite:///./ai_workbench.db"
    UPLOAD_DIR: str = "../data/uploads"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
