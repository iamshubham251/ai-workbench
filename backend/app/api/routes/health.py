from fastapi import APIRouter
from app.config.settings import settings
from app.services.sentence_transformer_embedding_provider import _GLOBAL_MODEL

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    return {
        "status": "ok", 
        "message": "Backend is running",
        "gemini_api_configured": bool(settings.GEMINI_API_KEY),
        "model_name": settings.GEMINI_MODEL,
        "embedding_model_ready": _GLOBAL_MODEL is not None,
    }
