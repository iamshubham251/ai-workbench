"""Agent execution routes."""

from uuid import uuid4

from fastapi import APIRouter, Depends

from app.agents.agent_manager import AgentManager
from app.dependencies import get_agent_manager
from app.models.agent import AgentTask
from app.schemas.agent import AgentExecuteRequest, AgentExecuteResponse


router = APIRouter()


@router.post(
    "/execute",
    response_model=AgentExecuteResponse,
)
def execute_agent(
    request: AgentExecuteRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
) -> AgentExecuteResponse:
    """Execute an agent task through the configured model router."""

    task = AgentTask(
        task_id=uuid4(),
        instruction=request.instruction,
        document_ids=request.document_ids,
    )

    result = agent_manager.execute(task)

    return AgentExecuteResponse(
        task_id=result.task_id,
        status=result.status,
        output=result.output,
        error=result.error,
    )
