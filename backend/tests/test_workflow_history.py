import pytest
from uuid import uuid4
from datetime import datetime
from app.models.workflow_run import WorkflowRun
from app.repositories.workflow_run_repository import WorkflowRunRepository

def test_workflow_history_empty(client):
    response = client.get("/api/workflows/history")
    assert response.status_code == 200
    assert response.json() == []

def test_workflow_history_unauthenticated():
    from fastapi.testclient import TestClient
    from app.main import app
    unauth_client = TestClient(app)
    response = unauth_client.get("/api/workflows/history")
    assert response.status_code == 401

def test_workflow_run_persistence(client):
    # Upload a document first
    file_bytes = b"%PDF-1.4 fake pdf"
    upload_res = client.post(
        "/api/documents/upload",
        files={"file": ("test.pdf", file_bytes, "application/pdf")},
    )
    assert upload_res.status_code == 200
    doc_id = upload_res.json()["id"]

    # Execute workflow (we expect 500 or 200 depending on FakeModelProvider, but here we can mock it)
    # Actually, we don't need to mock, let's just trigger it and check if it persists.
    # It might fail if real model is called, but we can mock get_approval_workflow_service
    from app.services.approval_workflow_service import ApprovalWorkflowService
    from app.services.gemini_inspection_analyzer import GeminiInspectionAnalyzer
    from app.models.approval_workflow import ApprovalWorkflowResult
    
    class DummyService:
        def execute_from_document(self, workflow_id, document_id, output_path):
            from app.models.approval_workflow import ApprovalWorkflowResult
            return ApprovalWorkflowResult(
                workflow_id=workflow_id,
                decision="approve",
                summary="Looks good",
                findings=(),
                supporting_evidence=()
            )

    from app.dependencies import get_approval_workflow_service
    client.app.dependency_overrides[get_approval_workflow_service] = lambda: DummyService()

    try:
        response = client.post(
            "/api/workflows/approval",
            json={
                "instruction": "test",
                "document_ids": [doc_id]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["decision"] == "approve"
        workflow_id = data["workflow_id"]

        # Check history
        history_res = client.get("/api/workflows/history")
        assert history_res.status_code == 200
        history = history_res.json()
        assert len(history) == 1
        assert history[0]["id"] == workflow_id
        assert history[0]["document_id"] == doc_id
        assert history[0]["document_name"] == "test.pdf"
        assert history[0]["decision"] == "approve"
        assert history[0]["status"] == "COMPLETED"
        assert history[0]["created_at"]
        assert history[0]["completed_at"]
    finally:
        client.app.dependency_overrides.pop(get_approval_workflow_service, None)

def test_workflow_run_persistence_failed(client):
    file_bytes = b"%PDF-1.4 fake pdf"
    upload_res = client.post(
        "/api/documents/upload",
        files={"file": ("test.pdf", file_bytes, "application/pdf")},
    )
    doc_id = upload_res.json()["id"]

    class FailingService:
        def execute_from_document(self, workflow_id, document_id, output_path):
            raise ValueError("Something broke")

    from app.dependencies import get_approval_workflow_service
    client.app.dependency_overrides[get_approval_workflow_service] = lambda: FailingService()

    try:
        response = client.post(
            "/api/workflows/approval",
            json={
                "instruction": "test",
                "document_ids": [doc_id]
            }
        )
        assert response.status_code == 500

        history_res = client.get("/api/workflows/history")
        history = history_res.json()
        
        # In history, there should be a FAILED run
        # Note: the user might have run previous tests, but order is newest first
        failed_run = history[0]
        assert failed_run["status"] == "FAILED"
        assert failed_run["document_id"] == doc_id
    finally:
        client.app.dependency_overrides.pop(get_approval_workflow_service, None)
