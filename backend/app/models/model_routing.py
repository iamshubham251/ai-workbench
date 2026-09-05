"""Domain types for AI Workbench model routing."""

from dataclasses import dataclass

from app.models.model import ModelCapability


@dataclass(frozen=True)
class ModelRoutingRequest:
    """Request used by the model router to select a model."""

    capability: ModelCapability
    prompt: str

    def __post_init__(self) -> None:
        if not self.prompt.strip():
            raise ValueError("prompt must not be empty")


@dataclass(frozen=True)
class ModelRoutingDecision:
    """Decision returned by the model router."""

    model_name: str
    capability: ModelCapability
