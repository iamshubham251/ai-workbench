from types import SimpleNamespace
from uuid import uuid4

from app.agents.agent_context_builder import AgentContextBuilder
from app.agents.agent_manager import AgentManager
from app.ai.deterministic_provider import DeterministicModelProvider
from app.ai.model_router import ModelRouter
from app.models.agent import AgentTask


class FakeRagService:
    def query_all(self, query, top_k):
        return SimpleNamespace(
            results=(
                SimpleNamespace(
                    document_id=uuid4(),
                    chunk_index=2,
                    text="Safety inspection requires supervisor approval.",
                    score=0.91,
                    page_numbers=(4,),
                    section_title="Approval Requirements",
                ),
            )
        )


def test_agent_manager_builds_grounded_prompt():
    manager = AgentManager(
        model_router=ModelRouter(
            providers=(DeterministicModelProvider(),)
        ),
        context_builder=AgentContextBuilder(FakeRagService()),
    )

    result = manager.execute(
        AgentTask(
            task_id=uuid4(),
            instruction="Determine whether approval is required.",
        )
    )

    assert result.status.value == "completed"
    assert "Determine whether approval is required." in result.output
    assert "Safety inspection requires supervisor approval." in result.output
    assert "Approval Requirements" in result.output
    assert "page(s) 4" in result.output
