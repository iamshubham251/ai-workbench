"""Tests for AI Workbench model domain types."""

import pytest

from app.models.model import (
    ModelCapability,
    ModelRequest,
    ModelResponse,
)


def test_model_capabilities_are_defined():
    assert ModelCapability.DOCUMENT.value == "document"
    assert ModelCapability.CODE.value == "code"


def test_model_request_accepts_prompt():
    request = ModelRequest(prompt="Summarize this inspection report.")

    assert request.prompt == "Summarize this inspection report."


def test_model_request_rejects_empty_prompt():
    with pytest.raises(ValueError, match="prompt must not be empty"):
        ModelRequest(prompt="   ")


def test_model_response_accepts_output():
    response = ModelResponse(
        output="The report contains three findings.",
        model_name="document-model",
    )

    assert response.output == "The report contains three findings."
    assert response.model_name == "document-model"


def test_model_response_rejects_empty_output():
    with pytest.raises(ValueError, match="output must not be empty"):
        ModelResponse(
            output="   ",
            model_name="document-model",
        )


def test_model_response_rejects_empty_model_name():
    with pytest.raises(ValueError, match="model_name must not be empty"):
        ModelResponse(
            output="Some output",
            model_name="   ",
        )
