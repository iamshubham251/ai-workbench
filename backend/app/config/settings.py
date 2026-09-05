from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Workbench"
    APP_ENV: str = "development"
    MAX_UPLOAD_SIZE_MB: int = 25
    DATABASE_PATH: str = "./ai_workbench.db"
    UPLOAD_DIR: str = "../data/uploads"
    OUTPUT_DIR: str = "../data/outputs"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
    ]

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"

    model_config = {
        "env_file": PROJECT_ROOT / ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
