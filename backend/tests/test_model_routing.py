"""Tests for AI Workbench model routing types."""

import pytest

from app.models.model import ModelCapability
from app.models.model_routing import (
    ModelRoutingDecision,
    ModelRoutingRequest,
)


def test_routing_request_accepts_document_capability():
    request = ModelRoutingRequest(
        capability=ModelCapability.DOCUMENT,
        prompt="Review the inspection report.",
    )

    assert request.capability == ModelCapability.DOCUMENT
    assert request.prompt == "Review the inspection report."


def test_routing_request_accepts_code_capability():
    request = ModelRoutingRequest(
        capability=ModelCapability.CODE,
        prompt="Fix this Python function.",
    )

    assert request.capability == ModelCapability.CODE
    assert request.prompt == "Fix this Python function."


def test_routing_request_rejects_empty_prompt():
    with pytest.raises(ValueError, match="prompt must not be empty"):
        ModelRoutingRequest(
            capability=ModelCapability.DOCUMENT,
            prompt="   ",
        )


def test_routing_decision_contains_selected_model():
    decision = ModelRoutingDecision(
        model_name="document-model",
        capability=ModelCapability.DOCUMENT,
    )

    assert decision.model_name == "document-model"
    assert decision.capability == ModelCapability.DOCUMENT
