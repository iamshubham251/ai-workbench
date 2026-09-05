"""
Backend test suite for Phase 3 — Document Ingestion.
Tests: health, upload (PDF/DOCX), validation, listing, retrieval,
       404, path traversal, oversized file, empty file.
"""

import pytest
from tests.conftest import (
    make_file,
    PDF_BYTES,
    DOCX_BYTES,
    DOCX_MIME,
    XLSX_MIME,
    PPTX_MIME,
)


# ==========================================================================
# 1. Health endpoint
# ==========================================================================

def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ==========================================================================
# 2. Successful PDF upload
# ==========================================================================

def test_upload_pdf_success(client):
    r = client.post(
        "/api/documents/upload",
        files=[make_file(PDF_BYTES, "inspection_report.pdf", "application/pdf")],
    )
    assert r.status_code == 201
    body = r.json()
    assert body["original_filename"] == "inspection_report.pdf"
    assert body["extension"] == ".pdf"
    assert body["status"] == "uploaded"
    assert "storage_path" not in body  # must not leak FS paths


# ==========================================================================
# 3. Successful DOCX upload
# ==========================================================================

def test_upload_docx_success(client):
    r = client.post(
        "/api/documents/upload",
        files=[make_file(DOCX_BYTES, "report.docx", DOCX_MIME)],
    )
    assert r.status_code == 201
    body = r.json()
    assert body["extension"] == ".docx"
    assert body["status"] == "uploaded"


# ==========================================================================
# 4. Unsupported extension
# ==========================================================================

def test_upload_unsupported_extension(client):
    r = client.post(
        "/api/documents/upload",
        files=[make_file(b"exe content", "malware.exe", "application/octet-stream")],
    )
    assert r.status_code == 415


# ==========================================================================
# 5. Unsupported media type (right extension, wrong MIME)
# ==========================================================================

def test_upload_mismatched_mime(client):
    r = client.post(
        "/api/documents/upload",
        files=[make_file(PDF_BYTES, "doc.pdf", "text/plain")],
    )
    assert r.status_code == 415


# ==========================================================================
# 6. Empty file
# ==========================================================================

def test_upload_empty_file(client):
    r = client.post(
        "/api/documents/upload",
        files=[make_file(b"", "empty.pdf", "application/pdf")],
    )
    assert r.status_code == 400


# ==========================================================================
# 7. Oversized file (limit is 1 MB in tests)
# ==========================================================================

def test_upload_oversized_file(client):
    big = b"A" * (2 * 1024 * 1024)  # 2 MB > 1 MB test limit
    r = client.post(
        "/api/documents/upload",
        files=[make_file(big, "big.pdf", "application/pdf")],
    )
    assert r.status_code == 413


# ==========================================================================
# 8. Document listing
# ==========================================================================

def test_list_documents(client):
    # Upload two documents
    client.post(
        "/api/documents/upload",
        files=[make_file(PDF_BYTES, "a.pdf", "application/pdf")],
    )
    client.post(
        "/api/documents/upload",
        files=[make_file(DOCX_BYTES, "b.docx", DOCX_MIME)],
    )
    r = client.get("/api/documents")
    assert r.status_code == 200
    assert len(r.json()) == 2


# ==========================================================================
# 9. Document retrieval by ID
# ==========================================================================

def test_get_document_by_id(client):
    upload = client.post(
        "/api/documents/upload",
        files=[make_file(PDF_BYTES, "report.pdf", "application/pdf")],
    )
    doc_id = upload.json()["id"]

    r = client.get(f"/api/documents/{doc_id}")
    assert r.status_code == 200
    assert r.json()["id"] == doc_id


# ==========================================================================
# 10. Non-existent document → 404
# ==========================================================================

def test_get_nonexistent_document(client):
    r = client.get("/api/documents/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


# ==========================================================================
# 11. Path traversal protection
# ==========================================================================

def test_path_traversal_in_filename(client, tmp_env):
    """
    A filename with path traversal sequences must be stored safely.
    - The file on disk must live inside the upload directory.
    - The stored filename must not contain traversal sequences.
    - original_filename is the raw display name — we do NOT assert on it here.
    """
    r = client.post(
        "/api/documents/upload",
        files=[make_file(PDF_BYTES, "../../etc/passwd.pdf", "application/pdf")],
    )
    # Must not cause a 500; accepted (sanitized) or rejected — both are OK.
    assert r.status_code in (201, 400, 415)

    if r.status_code == 201:
        doc_id = r.json()["id"]
        doc_dir = tmp_env["uploads"] / doc_id
        assert doc_dir.exists(), "Document directory was not created"

        # The file stored on disk must not contain traversal components
        for f in doc_dir.iterdir():
            assert ".." not in str(f), "Stored path contains traversal sequence"
            # Confirm the stored path is inside the upload dir
            assert str(f.resolve()).startswith(str(tmp_env["uploads"].resolve()))


# ==========================================================================
# 12. Extension / MIME cross-check (PDF ext + DOCX MIME)
# ==========================================================================

def test_extension_content_type_mismatch(client):
    r = client.post(
        "/api/documents/upload",
        files=[make_file(PDF_BYTES, "trick.pdf", DOCX_MIME)],
    )
    assert r.status_code == 400


# ==========================================================================
# 13. File exists on disk after upload
# ==========================================================================

def test_file_exists_on_disk(client, tmp_env):
    r = client.post(
        "/api/documents/upload",
        files=[make_file(PDF_BYTES, "check.pdf", "application/pdf")],
    )
    assert r.status_code == 201
    doc_id = r.json()["id"]

    # Verify file is actually on disk
    import os
    upload_root = tmp_env["uploads"]
    doc_dir = upload_root / doc_id
    assert doc_dir.exists(), "Document directory was not created"
    files = list(doc_dir.iterdir())
    assert len(files) == 1, "Expected exactly one stored file"


# ===========================================================================
# 14. Metadata failure rolls back the stored file
# ===========================================================================

def test_metadata_failure_cleans_up_stored_file(client, tmp_env, monkeypatch):
    from app.repositories.document_repository import DocumentRepository

    def fail_create(self, doc):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(DocumentRepository, "create", fail_create)
    r = client.post(
        "/api/documents/upload",
        files=[make_file(PDF_BYTES, "rollback.pdf", "application/pdf")],
    )

    assert r.status_code == 500
    assert list(tmp_env["uploads"].iterdir()) == []


# ==========================================================================
# 15. DELETE document
# ==========================================================================

def test_delete_document(client):
    r = client.post(
        "/api/documents/upload",
        files=[make_file(PDF_BYTES, "to_delete.pdf", "application/pdf")],
    )
    doc_id = r.json()["id"]

    del_r = client.delete(f"/api/documents/{doc_id}")
    assert del_r.status_code == 204

    get_r = client.get(f"/api/documents/{doc_id}")
    assert get_r.status_code == 404

# ==========================================================================
# RAG Query API
# ==========================================================================

def test_knowledge_query_returns_semantic_results(client, tmp_path):
    """Upload, ingest, and semantically query a real PDF through the API."""
    import fitz

    pdf_path = tmp_path / "knowledge.pdf"

    pdf = fitz.open()
    page = pdf.new_page()
    page.insert_text(
        (72, 72),
        "Safety inspection procedure requires checking conveyor belt "
        "alignment, emergency stops, guarding, and belt joint condition.",
    )
    pdf.save(pdf_path)
    pdf.close()

    with pdf_path.open("rb") as file:
        upload_response = client.post(
            "/api/documents/upload",
            files=[
                (
                    "file",
                    (
                        "knowledge.pdf",
                        file,
                        "application/pdf",
                    ),
                )
            ],
        )

    assert upload_response.status_code == 201
    document_id = upload_response.json()["id"]

    ingest_response = client.post(
        f"/api/knowledge/{document_id}/ingest"
    )

    assert ingest_response.status_code == 200
    ingest_body = ingest_response.json()
    assert ingest_body["document_id"] == document_id
    assert ingest_body["chunk_count"] >= 1
    assert ingest_body["embedding_count"] == ingest_body["chunk_count"]

    query_response = client.post(
        f"/api/knowledge/{document_id}/query",
        json={
            "query": "What does the safety inspection procedure check?",
            "top_k": 3,
        },
    )

    assert query_response.status_code == 200

    query_body = query_response.json()
    assert query_body["answer"]
    assert "Safety inspection procedure requires checking" in query_body["answer"]
    assert "page(s): 1" in query_body["answer"]
    assert query_body["query"] == "What does the safety inspection procedure check?"
    assert query_body["result_count"] >= 1
    assert len(query_body["results"]) >= 1

    result = query_body["results"][0]
    assert result["document_id"] == document_id
    assert result["chunk_index"] >= 0
    assert result["text"]
    assert result["score"] > 0
    assert result["page_numbers"] == [1]

def test_knowledge_query_rejects_invalid_top_k(client):
    """The query API must reject top_k values outside its public contract."""
    from uuid import uuid4

    response = client.post(
        f"/api/knowledge/{uuid4()}/query",
        json={
            "query": "safety inspection",
            "top_k": 0,
        },
    )

    assert response.status_code == 422

def test_knowledge_query_rejects_empty_query(client):
    """The query API must reject an empty search query."""
    from uuid import uuid4

    response = client.post(
        f"/api/knowledge/{uuid4()}/query",
        json={
            "query": "",
            "top_k": 5,
        },
    )

    assert response.status_code == 422

def test_knowledge_query_missing_document_returns_404(client):
    """Querying a document that does not exist must return 404."""
    from uuid import uuid4

    response = client.post(
        f"/api/knowledge/{uuid4()}/query",
        json={
            "query": "safety inspection",
            "top_k": 5,
        },
    )

    assert response.status_code == 404
