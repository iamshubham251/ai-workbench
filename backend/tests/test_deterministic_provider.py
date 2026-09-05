"""Tests for the deterministic model provider."""

from app.ai.deterministic_provider import DeterministicModelProvider
from app.ai.model_provider import ModelProvider
from app.models.model import ModelCapability, ModelRequest


def test_deterministic_provider_implements_provider_contract():
    provider = DeterministicModelProvider()

    assert isinstance(provider, ModelProvider)


def test_deterministic_provider_exposes_name():
    provider = DeterministicModelProvider()

    assert provider.name == "deterministic-model"


def test_deterministic_provider_supports_document_and_code():
    provider = DeterministicModelProvider()

    assert provider.capabilities == (
        ModelCapability.DOCUMENT,
        ModelCapability.CODE,
    )


def test_deterministic_provider_generates_response():
    provider = DeterministicModelProvider()

    response = provider.generate(
        ModelRequest(prompt="Review the inspection report.")
    )

    assert response.output == "Model response: Review the inspection report."
    assert response.model_name == "deterministic-model"


def test_deterministic_provider_preserves_prompt():
    provider = DeterministicModelProvider()
    prompt = "Generate an approval note from the findings."

    response = provider.generate(ModelRequest(prompt=prompt))

    assert prompt in response.output
