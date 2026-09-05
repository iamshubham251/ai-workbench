"""Model provider interface for AI Workbench."""

from typing import Protocol, runtime_checkable

from app.models.model import (
    ModelCapability,
    ModelRequest,
    ModelResponse,
)


class ModelProviderError(RuntimeError):
    """Raised when a model provider cannot process a request."""


@runtime_checkable
class ModelProvider(Protocol):
    """Interface implemented by every AI model provider."""

    @property
    def name(self) -> str:
        """Return the provider's model name."""
        ...

    @property
    def capabilities(self) -> tuple[ModelCapability, ...]:
        """Return capabilities supported by the model."""
        ...

    def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate a response for a model request."""
        ...

