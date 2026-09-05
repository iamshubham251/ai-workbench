"""Model Router for AI Workbench."""

from app.ai.model_provider import ModelProvider
from app.models.model import ModelCapability
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
        """Select the provider supporting the requested capability."""

        provider = self.get_provider(request.capability)

        return ModelRoutingDecision(
            model_name=provider.name,
            capability=request.capability,
        )

    def get_provider(self, capability: ModelCapability) -> ModelProvider:
        """Return the provider registered for a capability."""

        for provider in self._providers:
            if capability in provider.capabilities:
                return provider

        raise ModelRoutingError(
            f"No model provider supports capability "
            f"'{capability.value}'."
        )

    def _validate_providers(self) -> None:
        """Reject ambiguous provider registrations."""

        registered_capabilities: set[ModelCapability] = set()

        for provider in self._providers:
            for capability in provider.capabilities:
                if capability in registered_capabilities:
                    raise ModelRoutingError(
                        f"Multiple model providers registered for "
                        f"capability '{capability.value}'."
                    )
                registered_capabilities.add(capability)
