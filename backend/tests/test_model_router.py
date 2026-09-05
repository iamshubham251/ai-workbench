"""Tests for the AI Workbench Model Router."""

import pytest

from app.ai.model_provider import ModelProvider
from app.ai.model_router import ModelRouter, ModelRoutingError
from app.models.model import ModelCapability, ModelRequest, ModelResponse
from app.models.model_routing import ModelRoutingRequest


class FakeDocumentModel:
    @property
    def name(self) -> str:
        return "fake-document-model"

    @property
    def capabilities(self) -> tuple[ModelCapability, ...]:
        return (ModelCapability.DOCUMENT,)

    def generate(self, request: ModelRequest) -> ModelResponse:
        return ModelResponse(
            output=f"Document response: {request.prompt}",
            model_name=self.name,
        )


class FakeCodingModel:
    @property
    def name(self) -> str:
        return "fake-coding-model"

    @property
    def capabilities(self) -> tuple[ModelCapability, ...]:
        return (ModelCapability.CODE,)

    def generate(self, request: ModelRequest) -> ModelResponse:
        return ModelResponse(
            output=f"Code response: {request.prompt}",
            model_name=self.name,
        )


def test_model_router_selects_document_model():
    router = ModelRouter(providers=(FakeDocumentModel(), FakeCodingModel()))
    decision = router.route(
        ModelRoutingRequest(
            capability=ModelCapability.DOCUMENT,
            prompt="Review the inspection report.",
        )
    )
    assert decision.model_name == "fake-document-model"
    assert decision.capability == ModelCapability.DOCUMENT


def test_model_router_selects_coding_model():
    router = ModelRouter(providers=(FakeDocumentModel(), FakeCodingModel()))
    decision = router.route(
        ModelRoutingRequest(
            capability=ModelCapability.CODE,
            prompt="Fix this Python function.",
        )
    )
    assert decision.model_name == "fake-coding-model"
    assert decision.capability == ModelCapability.CODE


def test_model_router_returns_selected_provider():
    document_model = FakeDocumentModel()
    router = ModelRouter(providers=(document_model, FakeCodingModel()))

    provider = router.get_provider(ModelCapability.DOCUMENT)

    assert provider is document_model


def test_model_router_returns_coding_provider():
    coding_model = FakeCodingModel()
    router = ModelRouter(providers=(FakeDocumentModel(), coding_model))

    provider = router.get_provider(ModelCapability.CODE)

    assert provider is coding_model


def test_model_router_rejects_unsupported_capability():
    router = ModelRouter(providers=(FakeDocumentModel(),))

    with pytest.raises(
        ModelRoutingError,
        match="No model provider supports capability 'code'",
    ):
        router.route(
            ModelRoutingRequest(
                capability=ModelCapability.CODE,
                prompt="Fix this Python function.",
            )
        )


def test_model_router_get_provider_rejects_unsupported_capability():
    router = ModelRouter(providers=(FakeDocumentModel(),))

    with pytest.raises(
        ModelRoutingError,
        match="No model provider supports capability 'code'",
    ):
        router.get_provider(ModelCapability.CODE)


def test_model_router_rejects_duplicate_capability():
    with pytest.raises(
        ModelRoutingError,
        match="Multiple model providers registered for capability 'document'",
    ):
        ModelRouter(
            providers=(FakeDocumentModel(), FakeDocumentModel())
        )


def test_model_router_accepts_empty_provider_registry():
    router = ModelRouter()

    with pytest.raises(
        ModelRoutingError,
        match="No model provider supports capability 'document'",
    ):
        router.route(
            ModelRoutingRequest(
                capability=ModelCapability.DOCUMENT,
                prompt="Review the report.",
            )
        )


def test_fake_models_implement_provider_contract():
    assert isinstance(FakeDocumentModel(), ModelProvider)
    assert isinstance(FakeCodingModel(), ModelProvider)
