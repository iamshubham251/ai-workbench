"""Tests for the AI Workbench Agent Manager."""

from uuid import uuid4

from app.agents.agent_manager import AgentManager
from app.models.agent import AgentStatus, AgentTask


def test_agent_manager_executes_task():
    task_id = uuid4()
    task = AgentTask(
        task_id=task_id,
        instruction="Review the inspection report.",
    )

    result = AgentManager().execute(task)

    assert result.task_id == task_id
    assert result.status == AgentStatus.COMPLETED
    assert result.output == "Review the inspection report."
    assert result.error is None


def test_agent_manager_preserves_document_ids():
    document_id = uuid4()

    task = AgentTask(
        task_id=uuid4(),
        instruction="Review the inspection report.",
        document_ids=(document_id,),
    )

    result = AgentManager().execute(task)

    assert result.status == AgentStatus.COMPLETED
    assert result.task_id == task.task_id
