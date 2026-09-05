"""Tests for the AI Workbench model provider contract."""

from app.ai.model_provider import ModelProvider, ModelProviderError
from app.models.model import (
    ModelCapability,
    ModelRequest,
    ModelResponse,
)


class FakeDocumentModel:
    """Minimal provider implementation used for contract testing."""

    @property
    def name(self) -> str:
        return "fake-document-model"

    @property
    def capabilities(self) -> tuple[ModelCapability, ...]:
        return (ModelCapability.DOCUMENT,)

    def generate(self, request: ModelRequest) -> ModelResponse:
        return ModelResponse(
            output=f"Processed: {request.prompt}",
            model_name=self.name,
        )


def test_fake_provider_implements_model_provider():
    provider = FakeDocumentModel()

    assert isinstance(provider, ModelProvider)
    assert provider.name == "fake-document-model"
    assert provider.capabilities == (ModelCapability.DOCUMENT,)


def test_provider_generates_model_response():
    provider = FakeDocumentModel()

    response = provider.generate(
        ModelRequest(prompt="Summarize the report.")
    )

    assert response.output == "Processed: Summarize the report."
    assert response.model_name == "fake-document-model"


def test_model_provider_error_is_runtime_error():
    error = ModelProviderError("Model unavailable.")

    assert isinstance(error, RuntimeError)
    assert str(error) == "Model unavailable."
