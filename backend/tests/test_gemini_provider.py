from types import SimpleNamespace

import pytest

from app.ai.gemini_provider import GeminiModelProvider
from app.ai.model_provider import ModelProviderError
from app.models.model import ModelCapability, ModelRequest


class FakeInteractions:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.response


class FakeClient:
    def __init__(self, response=None, error=None):
        self.interactions = FakeInteractions(response=response, error=error)


def test_gemini_provider_exposes_expected_identity_and_capabilities():
    provider = GeminiModelProvider(
        model_name="test-gemini",
        client=FakeClient(),
    )

    assert provider.name == "test-gemini"
    assert provider.capabilities == (
        ModelCapability.DOCUMENT,
        ModelCapability.CODE,
    )


def test_gemini_provider_generates_response():
    fake_client = FakeClient(
        response=SimpleNamespace(output_text="  Gemini result  ")
    )
    provider = GeminiModelProvider(
        model_name="test-gemini",
        client=fake_client,
    )

    response = provider.generate(ModelRequest(prompt="Summarize this document."))

    assert response.output == "Gemini result"
    assert response.model_name == "test-gemini"
    assert fake_client.interactions.calls == [
        {
            "model": "test-gemini",
            "input": "Summarize this document.",
        }
    ]


def test_gemini_provider_rejects_empty_response():
    provider = GeminiModelProvider(
        model_name="test-gemini",
        client=FakeClient(response=SimpleNamespace(output_text="")),
    )

    with pytest.raises(ModelProviderError, match="empty response"):
        provider.generate(ModelRequest(prompt="Test"))


def test_gemini_provider_wraps_api_errors():
    provider = GeminiModelProvider(
        model_name="test-gemini",
        client=FakeClient(error=RuntimeError("API unavailable")),
    )

    with pytest.raises(ModelProviderError, match="Gemini generation failed"):
        provider.generate(ModelRequest(prompt="Test"))


def test_gemini_provider_requires_api_key_without_injected_client():
    with pytest.raises(ModelProviderError, match="GEMINI_API_KEY"):
        GeminiModelProvider(api_key="")
