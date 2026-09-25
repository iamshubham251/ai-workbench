from types import SimpleNamespace

import pytest

from app.ai.gemini_provider import GeminiModelProvider
from app.ai.model_provider import ModelProviderError
from app.models.model import ModelCapability, ModelRequest


class FakeModels:
    def __init__(self, response=None, error=None, failures_before_success=0):
        self.interactions = FakeInteractions(response=response, error=error, failures_before_success=failures_before_success)

    def generate_content(self, **kwargs):
        return self.interactions.create(**kwargs)


class FakeInteractions:
    def __init__(self, response=None, error=None, failures_before_success=0):
        self.response = response
        self.error = error
        self.failures_before_success = failures_before_success
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if len(self.calls) <= self.failures_before_success:
            raise self.error
        if self.error and self.failures_before_success == 0:
            raise self.error
        return self.response


class FakeClient:
    def __init__(self, response=None, error=None, failures_before_success=0):
        self.models = FakeModels(response=response, error=error, failures_before_success=failures_before_success)


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
    fake_client = FakeClient(response=SimpleNamespace(text="  Gemini result  "))
    provider = GeminiModelProvider(
        model_name="test-gemini",
        client=fake_client,
    )

    response = provider.generate(ModelRequest(prompt="Summarize this document."))

    assert response.output == "Gemini result"
    assert response.model_name == "test-gemini"
    assert fake_client.models.interactions.calls == [
        {
            "model": "test-gemini",
            "contents": "Summarize this document.",
        }
    ]


def test_gemini_provider_wraps_api_errors():
    provider = GeminiModelProvider(
        model_name="test-gemini",
        client=FakeClient(error=RuntimeError("API permanently unavailable")),
    )

    with pytest.raises(ModelProviderError, match="Gemini generation failed"):
        provider.generate(ModelRequest(prompt="Test"))


def test_gemini_provider_retries_transient_errors():
    fake_client = FakeClient(
        response=SimpleNamespace(text="Retried success"), 
        error=RuntimeError("503 Service Unavailable"),
        failures_before_success=1
    )
    provider = GeminiModelProvider(
        model_name="test-gemini",
        client=fake_client,
    )

    # Should succeed on the second attempt
    response = provider.generate(ModelRequest(prompt="Test retry"))
    assert response.output == "Retried success"
    assert len(fake_client.models.interactions.calls) == 2


def test_gemini_provider_exhausts_retries():
    fake_client = FakeClient(
        response=SimpleNamespace(text="Should not reach"), 
        error=RuntimeError("429 Too Many Requests"),
        failures_before_success=5 # More than max_retries (2)
    )
    provider = GeminiModelProvider(
        model_name="test-gemini",
        client=fake_client,
    )

    with pytest.raises(ModelProviderError, match="Gemini generation failed: 429 Too Many Requests"):
        provider.generate(ModelRequest(prompt="Test exhausted"))
        
    assert len(fake_client.models.interactions.calls) == 3 # Initial + 2 retries


def test_gemini_provider_requires_api_key_without_injected_client():
    with pytest.raises(ModelProviderError, match="GEMINI_API_KEY"):
        GeminiModelProvider(api_key="")
