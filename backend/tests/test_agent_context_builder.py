from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.agents.agent_context_builder import AgentContextBuilder


def make_result(document_id, chunk_index=0):
    return SimpleNamespace(
        document_id=document_id,
        chunk_index=chunk_index,
        text=f"Evidence {chunk_index}",
        score=0.9,
        page_numbers=(1,),
        section_title="Findings",
    )


class FakeRagService:
    def __init__(self):
        self.document_queries = []
        self.global_queries = []

    def query(self, document_id, query, top_k):
        self.document_queries.append((document_id, query, top_k))
        return SimpleNamespace(
            results=(make_result(document_id),)
        )

    def query_all(self, query, top_k):
        self.global_queries.append((query, top_k))
        return SimpleNamespace(
            results=(make_result(uuid4()),)
        )


def test_builds_context_for_specific_documents():
    rag = FakeRagService()
    builder = AgentContextBuilder(rag)

    document_id = uuid4()

    context = builder.build(
        instruction="Find inspection failures.",
        document_ids=(document_id,),
        top_k=3,
    )

    assert context.item_count == 1
    assert context.has_evidence
    assert context.items[0].document_id == document_id
    assert context.items[0].text == "Evidence 0"
    assert rag.document_queries == [
        (document_id, "Find inspection failures.", 3)
    ]
    assert rag.global_queries == []


def test_builds_context_from_global_knowledge_base():
    rag = FakeRagService()
    builder = AgentContextBuilder(rag)

    context = builder.build(
        instruction="Find relevant safety requirements.",
        top_k=4,
    )

    assert context.item_count == 1
    assert context.has_evidence
    assert rag.global_queries == [
        ("Find relevant safety requirements.", 4)
    ]
    assert rag.document_queries == []


def test_queries_each_requested_document():
    rag = FakeRagService()
    builder = AgentContextBuilder(rag)

    document_ids = (uuid4(), uuid4())

    context = builder.build(
        instruction="Compare findings.",
        document_ids=document_ids,
    )

    assert context.item_count == 2
    assert [item.document_id for item in context.items] == list(document_ids)
    assert len(rag.document_queries) == 2


def test_rejects_empty_instruction():
    rag = FakeRagService()
    builder = AgentContextBuilder(rag)

    with pytest.raises(ValueError, match="instruction must not be empty"):
        builder.build("   ")


def test_rejects_invalid_top_k():
    rag = FakeRagService()
    builder = AgentContextBuilder(rag)

    with pytest.raises(ValueError, match="top_k must be at least 1"):
        builder.build("Find evidence.", top_k=0)
