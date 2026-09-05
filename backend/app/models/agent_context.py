"""Domain types for agent grounding context."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AgentContextItem:
    """A piece of retrieved evidence supplied to an agent."""

    document_id: UUID
    chunk_index: int
    text: str
    score: float
    page_numbers: tuple[int, ...] = ()
    section_title: str | None = None


@dataclass(frozen=True)
class AgentContext:
    """Retrieved evidence assembled for an agent task."""

    items: tuple[AgentContextItem, ...] = ()

    @property
    def item_count(self) -> int:
        return len(self.items)

    @property
    def has_evidence(self) -> bool:
        return bool(self.items)
