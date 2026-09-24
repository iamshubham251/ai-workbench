import os
import sentry_sdk
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator

from app.config.settings import settings
from app.api.routes import (
    agents,
    documents,
    health,
    knowledge,
    knowledge_query,
    workflows,
)
from app.repositories.document_repository import DocumentRepository

# Configure Structured Logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
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

    app.include_router(health.router, prefix="/api")
    app.include_router(
        documents.router,
        prefix="/api/documents",
        tags=["documents"],
    )
    app.include_router(
        knowledge.router,
        prefix="/api/knowledge",
        tags=["knowledge"],
    )
    app.include_router(
        knowledge_query.router,
        prefix="/api/knowledge",
        tags=["knowledge"],
    )
    app.include_router(
        agents.router,
        prefix="/api/agents",
        tags=["agents"],
    )
    app.include_router(
        workflows.router,
        prefix="/api/workflows",
        tags=["workflows"],
    )

    return app


app = create_app()
