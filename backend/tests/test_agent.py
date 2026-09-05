"""Tests for AI Workbench agent domain types."""

from uuid import uuid4

import pytest

from app.models.agent import AgentResult, AgentStatus, AgentTask


def test_agent_task_accepts_instruction():
    task_id = uuid4()

    task = AgentTask(
        task_id=task_id,
        instruction="Review the inspection report.",
    )

    assert task.task_id == task_id
    assert task.instruction == "Review the inspection report."
    assert task.document_ids == ()


def test_agent_task_accepts_document_ids():
    task_id = uuid4()
    document_id = uuid4()

    task = AgentTask(
        task_id=task_id,
        instruction="Review the inspection report.",
        document_ids=(document_id,),
    )

    assert task.document_ids == (document_id,)


def test_agent_task_rejects_empty_instruction():
    with pytest.raises(ValueError, match="instruction must not be empty"):
        AgentTask(
            task_id=uuid4(),
            instruction="   ",
        )


def test_completed_agent_result_requires_output():
    with pytest.raises(
        ValueError,
        match="completed agent result must contain output",
    ):
        AgentResult(
            task_id=uuid4(),
            status=AgentStatus.COMPLETED,
        )


def test_failed_agent_result_requires_error():
    with pytest.raises(
        ValueError,
        match="failed agent result must contain error",
    ):
        AgentResult(
            task_id=uuid4(),
            status=AgentStatus.FAILED,
        )


def test_completed_agent_result_accepts_output():
    task_id = uuid4()

    result = AgentResult(
        task_id=task_id,
        status=AgentStatus.COMPLETED,
        output="Inspection reviewed successfully.",
    )

    assert result.task_id == task_id
    assert result.status == AgentStatus.COMPLETED
    assert result.output == "Inspection reviewed successfully."
    assert result.error is None
