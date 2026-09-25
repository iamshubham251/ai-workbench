import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.ai.model_provider import ModelProviderError
from app.services.pypdf_processor import PdfProcessingError
from fastapi import APIRouter

app = create_app()
router = APIRouter()

@router.get("/test-503")
def raise_503():
    raise ModelProviderError("Gemini generation failed: 503 UNAVAILABLE.")

@router.get("/test-500")
def raise_500():
    raise ModelProviderError("Gemini generation failed: Unknown Error.")

@router.get("/test-pdf-error")
def raise_pdf_error():
    raise PdfProcessingError("Invalid PDF format")

@router.get("/test-client-error")
def raise_value_error():
    raise ValueError("Empty string provided")

app.include_router(router)
client = TestClient(app)

def test_structured_error_503_transient():
    response = client.get("/test-503")
    assert response.status_code == 503
    data = response.json()
    assert data["code"] == "MODEL_PROVIDER_UNAVAILABLE"
    assert "temporarily unavailable" in data["detail"]

def test_structured_error_500_permanent():
    response = client.get("/test-500")
    assert response.status_code == 500
    data = response.json()
    assert data["code"] == "MODEL_PROVIDER_ERROR"
    assert "unexpected error" in data["detail"]

def test_structured_error_pdf():
    response = client.get("/test-pdf-error")
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "PDF_PROCESSING_ERROR"
    assert "could not be processed" in data["detail"]

def test_structured_error_value():
    response = client.get("/test-client-error")
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "INVALID_REQUEST"
    assert "Empty string provided" in data["detail"]
