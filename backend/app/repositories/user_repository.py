from uuid import UUID, uuid4
from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.database import get_connection
from app.models.user import User

class UserRepository:
    def __init__(self) -> None:
        self._create_table()

    def _get_connection(self) -> Connection:
        return get_connection()

    def _create_table(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(36) PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1
                )
                """)
            )
            conn.commit()

    def get_by_email(self, email: str) -> User | None:
        with self._get_connection() as conn:
            row = conn.execute(
                text("SELECT * FROM users WHERE email = :email"),
                {"email": email}
            ).fetchone()
        
        if not row:
            return None
        
        return User(
            id=UUID(row._mapping["id"]),
            email=row._mapping["email"],
            hashed_password=row._mapping["hashed_password"],
            is_active=bool(row._mapping["is_active"]),
        )

    def create(self, email: str, hashed_password: str) -> User:
        user = User(
            id=uuid4(),
            email=email,
            hashed_password=hashed_password,
            is_active=True
        )
        with self._get_connection() as conn:
            conn.execute(
                text("""
                INSERT INTO users (id, email, hashed_password, is_active)
                VALUES (:id, :email, :hashed_password, :is_active)
                """),
                {
                    "id": str(user.id),
                    "email": user.email,
                    "hashed_password": user.hashed_password,
                    "is_active": user.is_active
                }
            )
            conn.commit()
        return user
