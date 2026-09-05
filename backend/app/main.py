from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.api.routes import health, documents, knowledge
from app.repositories.document_repository import DocumentRepository


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def initialize_database() -> None:
        """Create the local metadata schema before accepting requests."""
        DocumentRepository(db_path=settings.DATABASE_PATH)

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

    return app


app = create_app()
