"""Agent Manager for AI Workbench task execution."""

from app.agents.agent_context_builder import AgentContextBuilder
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
        context_builder: AgentContextBuilder | None = None,
    ) -> None:
        self._model_router = model_router or ModelRouter()
        self._context_builder = context_builder

    def execute(self, task: AgentTask) -> AgentResult:
        """Route an agent task with optional grounded knowledge context."""

        try:
            prompt = task.instruction

            if self._context_builder is not None:
                context = self._context_builder.build(
                    instruction=task.instruction,
                    document_ids=task.document_ids,
                )
                prompt = self._build_grounded_prompt(
                    instruction=task.instruction,
                    context=context,
                )

            routing_request = ModelRoutingRequest(
                capability=ModelCapability.DOCUMENT,
                prompt=prompt,
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

    @staticmethod
    def _build_grounded_prompt(instruction: str, context) -> str:
        """Build a prompt that clearly separates instructions from evidence."""

        if not context.has_evidence:
            return (
                "You are an AI Workbench document agent.\n\n"
                "Task:\n"
                f"{instruction}\n\n"
                "No supporting evidence was found in the local knowledge base. "
                "Do not invent facts."
            )

        evidence_blocks = []

        for index, item in enumerate(context.items, start=1):
            source = f"Document {item.document_id}, chunk {item.chunk_index}"

            if item.page_numbers:
                pages = ", ".join(str(page) for page in item.page_numbers)
                source += f", page(s) {pages}"

            if item.section_title:
                source += f", section: {item.section_title}"

            evidence_blocks.append(
                f"[Evidence {index} | {source} | score={item.score:.3f}]\n"
                f"{item.text}"
            )

        evidence = "\n\n".join(evidence_blocks)

        return (
            "You are an AI Workbench document agent.\n\n"
            "Task:\n"
            f"{instruction}\n\n"
            "Use the following local knowledge-base evidence to answer the task.\n"
            "Treat the evidence as the source of truth. "
            "Do not invent unsupported facts.\n\n"
            f"{evidence}"
        )
