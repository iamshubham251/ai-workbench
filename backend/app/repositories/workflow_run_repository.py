from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.database import get_connection
from app.models.workflow_run import WorkflowRun

class WorkflowRunRepository:
    DDL = """
        CREATE TABLE IF NOT EXISTS workflow_runs (
            id VARCHAR(36) PRIMARY KEY,
            document_id VARCHAR(36),
            user_id VARCHAR(36) NOT NULL,
            status VARCHAR(50) NOT NULL,
            decision VARCHAR(50),
            error_message TEXT,
            output_path VARCHAR(500),
            created_at VARCHAR(50) NOT NULL,
            completed_at VARCHAR(50)
        )
    """

    def __init__(self) -> None:
        self._init_schema()

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(text(self.DDL))
            conn.commit()

    def _connect(self) -> Connection:
        return get_connection()

    def create(self, run: WorkflowRun) -> WorkflowRun:
        with self._connect() as conn:
            conn.execute(
                text("""
                INSERT INTO workflow_runs (
                    id, document_id, user_id, status, decision,
                    error_message, output_path, created_at, completed_at
                ) VALUES (
                    :id, :document_id, :user_id, :status, :decision,
                    :error_message, :output_path, :created_at, :completed_at
                )
                """),
                {
                    "id": str(run.id),
                    "document_id": str(run.document_id) if run.document_id else None,
                    "user_id": str(run.user_id),
                    "status": run.status,
                    "decision": run.decision,
                    "error_message": run.error_message,
                    "output_path": run.output_path,
                    "created_at": run.created_at.isoformat(),
                    "completed_at": run.completed_at.isoformat() if run.completed_at else None,
                },
            )
            conn.commit()
        return run

    def update(self, run: WorkflowRun) -> WorkflowRun:
        with self._connect() as conn:
            conn.execute(
                text("""
                UPDATE workflow_runs SET
                    status = :status,
                    decision = :decision,
                    error_message = :error_message,
                    output_path = :output_path,
                    completed_at = :completed_at
                WHERE id = :id
                """),
                {
                    "id": str(run.id),
                    "status": run.status,
                    "decision": run.decision,
                    "error_message": run.error_message,
                    "output_path": run.output_path,
                    "completed_at": run.completed_at.isoformat() if run.completed_at else None,
                }
            )
            conn.commit()
        return run

    def list_by_user_with_document_name(self, user_id: UUID) -> List[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                text("""
                SELECT w.*, d.original_filename as document_name 
                FROM workflow_runs w
                LEFT JOIN documents d ON w.document_id = d.id
                WHERE w.user_id = :user_id 
                ORDER BY w.created_at DESC
                """),
                {"user_id": str(user_id)}
            ).fetchall()
            
        return [dict(r._mapping) for r in rows]
