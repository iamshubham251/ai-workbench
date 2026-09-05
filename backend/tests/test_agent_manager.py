"""Tests for the AI Workbench Agent Manager."""

from uuid import uuid4

from app.agents.agent_manager import AgentManager
from app.ai.deterministic_provider import DeterministicModelProvider
from app.ai.model_router import ModelRouter
from app.models.agent import AgentStatus, AgentTask


def create_agent_manager() -> AgentManager:
    """Create an Agent Manager with a deterministic document provider."""

    router = ModelRouter(
        providers=(DeterministicModelProvider(),)
    )
    return AgentManager(model_router=router)


def test_agent_manager_executes_task_through_model():
    task_id = uuid4()
    task = AgentTask(
        task_id=task_id,
        instruction="Review the inspection report.",
    )

    result = create_agent_manager().execute(task)

    assert result.task_id == task_id
    assert result.status == AgentStatus.COMPLETED
    assert result.output == "Model response: Review the inspection report."
    assert result.error is None


def test_agent_manager_preserves_document_ids():
    document_id = uuid4()

    task = AgentTask(
        task_id=uuid4(),
        instruction="Review the inspection report.",
        document_ids=(document_id,),
    )

    result = create_agent_manager().execute(task)

    assert result.status == AgentStatus.COMPLETED
    assert result.task_id == task.task_id


def test_agent_manager_fails_when_no_model_supports_task():
    task = AgentTask(
        task_id=uuid4(),
        instruction="Review the inspection report.",
    )

    result = AgentManager().execute(task)

    assert result.task_id == task.task_id
    assert result.status == AgentStatus.FAILED
    assert result.output == ""
    assert "No model provider supports capability 'document'" in result.error


def test_agent_manager_returns_provider_failure_as_agent_failure():
    class FailingProvider(DeterministicModelProvider):
        def generate(self, request):
            raise RuntimeError("model execution failed")

    manager = AgentManager(
        model_router=ModelRouter(
            providers=(FailingProvider(),)
        )
    )

    task = AgentTask(
        task_id=uuid4(),
        instruction="Review the inspection report.",
    )

    result = manager.execute(task)

    assert result.status == AgentStatus.FAILED
    assert result.error == "model execution failed"
