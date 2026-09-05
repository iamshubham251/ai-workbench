"""Domain types for AI Workbench agent execution."""

from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class AgentStatus(str, Enum):
    """Lifecycle states for an agent execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class AgentTask:
    """A single task submitted to the Agent Manager."""

    task_id: UUID
    instruction: str
    document_ids: tuple[UUID, ...] = ()

    def __post_init__(self) -> None:
        if not self.instruction.strip():
            raise ValueError("instruction must not be empty")


@dataclass(frozen=True)
class AgentResult:
    """Result produced by an agent execution."""

    task_id: UUID
    status: AgentStatus
    output: str = ""
    error: str | None = None

    def __post_init__(self) -> None:
        if self.status == AgentStatus.COMPLETED and not self.output.strip():
            raise ValueError("completed agent result must contain output")
        if self.status == AgentStatus.FAILED and not self.error:
            raise ValueError("failed agent result must contain error")
