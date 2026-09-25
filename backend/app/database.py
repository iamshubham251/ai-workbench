from sqlalchemy import create_engine
from app.config.settings import settings

_engine = None

def _get_engine():
    global _engine
    if _engine is None:
        db_url = settings.DATABASE_URL
        if not db_url:
            db_url = f"sqlite:///{settings.DATABASE_PATH}"
        connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
        _engine = create_engine(
            db_url,
            connect_args=connect_args,
            pool_pre_ping=True
        )
    return _engine

def get_connection():
    return _get_engine().connect()

def reset_engine():
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
