"""Schemas for agent execution requests and responses."""

from uuid import UUID

from pydantic import BaseModel, Field

from app.models.agent import AgentStatus


class AgentExecuteRequest(BaseModel):
    instruction: str = Field(min_length=1)
    document_ids: tuple[UUID, ...] = ()


class AgentExecuteResponse(BaseModel):
    task_id: UUID
    status: AgentStatus
    output: str = ""
    error: str | None = None
