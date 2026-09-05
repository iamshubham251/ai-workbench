"""Domain types for the inspection approval workflow."""

from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class ApprovalDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REVIEW = "review"


@dataclass(frozen=True)
class InspectionFinding:
    finding: str
    severity: str = ""
    page_number: int | None = None

    def __post_init__(self) -> None:
        if not self.finding.strip():
            raise ValueError("finding must not be empty")
        if self.page_number is not None and self.page_number < 1:
            raise ValueError("page_number must be one-based")


@dataclass(frozen=True)
class ApprovalWorkflowRequest:
    workflow_id: UUID
    instruction: str
    document_ids: tuple[UUID, ...] = ()

    def __post_init__(self) -> None:
        if not self.instruction.strip():
            raise ValueError("instruction must not be empty")


@dataclass(frozen=True)
class ApprovalWorkflowResult:
    workflow_id: UUID
    decision: ApprovalDecision
    summary: str
    supporting_evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.summary.strip():
            raise ValueError("summary must not be empty")
