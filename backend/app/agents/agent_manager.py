"""Agent Manager for AI Workbench task execution."""

from app.ai.model_provider import ModelProvider
from app.ai.model_router import ModelRouter
from app.models.agent import AgentResult, AgentStatus, AgentTask
from app.models.model import ModelCapability, ModelRequest
from app.models.model_routing import ModelRoutingRequest


class AgentManager:
    """Coordinate execution of AI Workbench agent tasks."""

    def __init__(
        self,
        model_router: ModelRouter | None = None,
    ) -> None:
        self._model_router = model_router or ModelRouter()

    def execute(self, task: AgentTask) -> AgentResult:
        """Route an agent task to the appropriate model and execute it."""

        try:
            routing_request = ModelRoutingRequest(
                capability=ModelCapability.DOCUMENT,
                prompt=task.instruction,
            )

            provider: ModelProvider = self._model_router.get_provider(
                routing_request.capability
            )

            response = provider.generate(
                ModelRequest(prompt=routing_request.prompt)
            )

            return AgentResult(
                task_id=task.task_id,
                status=AgentStatus.COMPLETED,
                output=response.output,
            )

        except Exception as exc:
            return AgentResult(
                task_id=task.task_id,
                status=AgentStatus.FAILED,
                error=str(exc),
            )
