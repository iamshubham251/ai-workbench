"""Model Router for AI Workbench."""

from app.ai.model_provider import ModelProvider
from app.models.model_routing import (
    ModelRoutingDecision,
    ModelRoutingRequest,
)


class ModelRoutingError(RuntimeError):
    """Raised when a suitable model cannot be selected."""


class ModelRouter:
    """Select a model provider based on requested capability."""

    def __init__(self, providers: tuple[ModelProvider, ...] = ()) -> None:
        self._providers = providers
        self._validate_providers()

    def route(self, request: ModelRoutingRequest) -> ModelRoutingDecision:
        """Select the first provider supporting the requested capability."""

        for provider in self._providers:
            if request.capability in provider.capabilities:
                return ModelRoutingDecision(
                    model_name=provider.name,
                    capability=request.capability,
                )

        raise ModelRoutingError(
            f"No model provider supports capability "
            f"'{request.capability.value}'."
        )

    def _validate_providers(self) -> None:
        """Reject ambiguous provider registrations."""

        registered_capabilities: set = set()

        for provider in self._providers:
            for capability in provider.capabilities:
                if capability in registered_capabilities:
                    raise ModelRoutingError(
                        f"Multiple model providers registered for "
                        f"capability '{capability.value}'."
                    )
                registered_capabilities.add(capability)
