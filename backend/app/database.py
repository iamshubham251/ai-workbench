from sqlalchemy import create_engine
from app.config.settings import settings

db_url = settings.DATABASE_URL
if not db_url:
    # Fallback to SQLite
    db_url = f"sqlite:///{settings.DATABASE_PATH}"

# For SQLite, we need check_same_thread=False
connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True
)

def get_connection():
    return engine.connect()
