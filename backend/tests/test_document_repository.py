from datetime import datetime, timezone
from uuid import uuid4

from app.models.document import Document, DocumentRole
from app.repositories.document_repository import DocumentRepository


def make_document(filename: str = "report.pdf", role: DocumentRole = DocumentRole.OTHER) -> Document:
    now = datetime.now(timezone.utc)
    return Document(
        id=uuid4(),
        original_filename=filename,
        stored_filename=filename,
        content_type="application/pdf",
        extension=".pdf",
        size_bytes=1024,
        status="uploaded",
        storage_path=f"/uploads/{filename}",
        created_at=now,
        updated_at=now,
        role=role,
    )


def test_create_and_get_document(tmp_path):
    repository = DocumentRepository(str(tmp_path / "documents.db"))
    document = make_document()

    created = repository.create(document)
    found = repository.get_by_id(document.id)

    assert created == document
    assert found == document


def test_get_nonexistent_document_returns_none(tmp_path):
    repository = DocumentRepository(str(tmp_path / "documents.db"))

    assert repository.get_by_id(uuid4()) is None


def test_list_documents_by_role_returns_only_matching_documents(tmp_path):
    repository = DocumentRepository(str(tmp_path / "documents.db"))
    sop = make_document("sop.pdf", role=DocumentRole.SOP)
    inspection = make_document(
        "inspection.pdf",
        role=DocumentRole.INSPECTION_REPORT,
    )

    repository.create(sop)
    repository.create(inspection)

    documents = repository.list_documents_by_role(DocumentRole.SOP)

    assert [document.id for document in documents] == [sop.id]


def test_list_documents_returns_all_documents_newest_first(tmp_path):
    repository = DocumentRepository(str(tmp_path / "documents.db"))
    first = make_document("first.pdf")
    second = make_document("second.pdf")
    repository.create(first)
    repository.create(second)

    documents = repository.list_documents()

    assert [document.id for document in documents] == [second.id, first.id]
