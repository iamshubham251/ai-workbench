from pathlib import Path

from fastapi.testclient import TestClient

from app.config.settings import settings
from app.dependencies import get_approval_workflow_service
from app.main import app
from app.services.approval_decision_service import ApprovalDecisionService
from app.services.approval_workflow_service import ApprovalWorkflowService
from app.services.gemini_inspection_analyzer import GeminiInspectionAnalyzer


class FakeModelProvider:
    @property
    def name(self):
        return "fake-model"

    @property
    def capabilities(self):
        return ()

    def generate(self, request):
        from app.models.model import ModelResponse

        return ModelResponse(
            output="- finding: Emergency stop is functional. | severity: low | page: 2",
            model_name=self.name,
        )


def test_approval_api_returns_decision_and_output():
    service = ApprovalWorkflowService(
        inspection_analyzer=GeminiInspectionAnalyzer(
            FakeModelProvider(),
        ),
    )

    app.dependency_overrides[get_approval_workflow_service] = lambda: service

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/workflows/approval",
                json={
                    "instruction": "Emergency stop inspection completed.",
                },
            )

        assert response.status_code == 200

        body = response.json()

        assert body["decision"] == "approve"
        assert body["summary"]
        assert body["workflow_id"]
        assert body["output_path"]

        output_path = Path(body["output_path"])

        assert output_path.exists()
        assert output_path.suffix == ".docx"
        assert output_path.parent == Path(settings.OUTPUT_DIR)

    finally:
        app.dependency_overrides.clear()
