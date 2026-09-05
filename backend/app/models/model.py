"""Domain types for AI Workbench model execution."""

from dataclasses import dataclass
from enum import Enum


class ModelCapability(str, Enum):
    """Capabilities that a model can provide."""

    DOCUMENT = "document"
    CODE = "code"


@dataclass(frozen=True)
class ModelRequest:
    """A request sent to an AI model."""

    prompt: str

    def __post_init__(self) -> None:
        if not self.prompt.strip():
            raise ValueError("prompt must not be empty")


@dataclass(frozen=True)
class ModelResponse:
    """Response returned by an AI model."""

    output: str
    model_name: str

    def __post_init__(self) -> None:
        if not self.output.strip():
            raise ValueError("output must not be empty")
        if not self.model_name.strip():
            raise ValueError("model_name must not be empty")
