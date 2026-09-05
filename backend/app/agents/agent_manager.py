"""Agent Manager for AI Workbench task execution."""

from app.models.agent import AgentResult, AgentStatus, AgentTask


class AgentManager:
    """Coordinate execution of AI Workbench agent tasks."""

    def execute(self, task: AgentTask) -> AgentResult:
        """Execute an agent task.

        The initial implementation provides the execution boundary only.
        Model routing, RAG, and tool execution will be integrated behind
        this boundary in later phases.
        """

        return AgentResult(
            task_id=task.task_id,
            status=AgentStatus.COMPLETED,
            output=task.instruction,
        )
