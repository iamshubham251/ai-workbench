from fastapi.testclient import TestClient

from app.agents.agent_manager import AgentManager
from app.ai.deterministic_provider import DeterministicModelProvider
from app.ai.model_router import ModelRouter
from app.dependencies import get_agent_manager
from app.main import app


def test_agent_execute_api():
    manager = AgentManager(
        model_router=ModelRouter(
            providers=(DeterministicModelProvider(),)
        )
    )

    app.dependency_overrides[get_agent_manager] = lambda: manager

    try:
        client = TestClient(app)

        response = client.post(
            "/api/agents/execute",
            json={
                "instruction": "Summarize the inspection findings.",
            },
        )

        assert response.status_code == 200

        body = response.json()
        assert body["status"] == "completed"
        assert body["output"] == (
            "Model response: Summarize the inspection findings."
        )
        assert body["task_id"]
        assert body["error"] is None
    finally:
        app.dependency_overrides.clear()
