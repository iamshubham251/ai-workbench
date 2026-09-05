"""Deterministic model provider for AI Workbench."""

from app.models.model import (
    ModelCapability,
    ModelRequest,
    ModelResponse,
)


class DeterministicModelProvider:
    """Simple provider used for deterministic local execution and testing."""

    @property
    def name(self) -> str:
        return "deterministic-model"

    @property
    def capabilities(self) -> tuple[ModelCapability, ...]:
        return (
            ModelCapability.DOCUMENT,
            ModelCapability.CODE,
        )

    def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate a deterministic response for a model request."""

        return ModelResponse(
            output=f"Model response: {request.prompt}",
            model_name=self.name,
        )
