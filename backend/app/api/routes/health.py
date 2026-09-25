from fastapi import APIRouter
from app.config.settings import settings

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    return {
        "status": "ok", 
        "message": "Backend is running",
        "model_configured": bool(settings.GEMINI_API_KEY),
        "model_name": settings.GEMINI_MODEL,
        "knowledge_base_configured": True,
    }
