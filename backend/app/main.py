import os

import sentry_sdk
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.routes import (
    agents,
    auth,
    documents,
    health,
    knowledge,
    knowledge_query,
    workflows,
)
from app.ai.model_provider import ModelProviderError
from app.services.pypdf_processor import PdfProcessingError
from app.config.settings import settings
from app.repositories.document_repository import DocumentRepository

# Configure Structured Logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
logger = structlog.get_logger()

# Initialize Sentry (Will only send errors if DSN is set in environment)
sentry_dsn = os.getenv("SENTRY_DSN", "")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )

    # Rate limiting setup
    limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    from fastapi.responses import JSONResponse
    from fastapi import Request

    @app.exception_handler(ModelProviderError)
    async def model_provider_exception_handler(request: Request, exc: ModelProviderError):
        logger.error("Model provider error", exc_info=exc)
        
        error_str = str(exc).lower()
        is_transient = any(
            term in error_str for term in ("503", "unavailable", "429", "timeout")
        )

        if is_transient:
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "The AI provider is temporarily unavailable. Please try again shortly.",
                    "code": "MODEL_PROVIDER_UNAVAILABLE"
                },
            )

        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred with the AI provider.",
                "code": "MODEL_PROVIDER_ERROR"
            },
        )

    @app.exception_handler(PdfProcessingError)
    async def pdf_processing_exception_handler(request: Request, exc: PdfProcessingError):
        logger.error("PDF processing error", exc_info=exc)
        return JSONResponse(
            status_code=422,
            content={
                "detail": "The provided PDF document could not be processed.",
                "code": "PDF_PROCESSING_ERROR"
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_exception_handler(request: Request, exc: ValueError):
        logger.warning("Client value error", exc_info=exc)
        return JSONResponse(
            status_code=400,
            content={
                "detail": str(exc),
                "code": "INVALID_REQUEST"
            },
        )

    # In production, ALLOWED_ORIGINS should be strictly defined in .env
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Instrument Prometheus Metrics
    Instrumentator().instrument(app).expose(app, endpoint="/api/metrics")

    @app.on_event("startup")
    def initialize_database() -> None:
        """Create the local metadata schema before accepting requests."""
        logger.info("Initializing database...")
        DocumentRepository(db_path=settings.DATABASE_PATH)
        logger.info("Database initialized successfully.")

    from fastapi import Depends
    from app.dependencies import get_current_user

    app.include_router(health.router, prefix="/api")
    app.include_router(
        auth.router,
        prefix="/api/auth",
        tags=["auth"],
    )
    app.include_router(
        documents.router,
        prefix="/api/documents",
        tags=["documents"],
        dependencies=[Depends(get_current_user)]
    )
    app.include_router(
        knowledge.router,
        prefix="/api/knowledge",
        tags=["knowledge"],
        dependencies=[Depends(get_current_user)]
    )
    app.include_router(
        knowledge_query.router,
        prefix="/api/knowledge",
        tags=["knowledge"],
        dependencies=[Depends(get_current_user)]
    )
    app.include_router(
        agents.router,
        prefix="/api/agents",
        tags=["agents"],
        dependencies=[Depends(get_current_user)]
    )
    app.include_router(
        workflows.router,
        prefix="/api/workflows",
        tags=["workflows"],
        dependencies=[Depends(get_current_user)]
    )

    return app


app = create_app()
