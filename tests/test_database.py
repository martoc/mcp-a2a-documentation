"""Tests for database operations."""

import tempfile
from pathlib import Path

from mcp_a2a_documentation.database import DocumentDatabase
from mcp_a2a_documentation.models import Document


def _make_doc(
    path: str,
    title: str = "Doc",
    content: str = "Content",
    section: str = "topics",
    source: str = "a2a",
    url: str = "https://a2a-protocol.org/latest/topics/",
    description: str | None = None,
) -> Document:
    return Document(
        path=path,
        title=title,
        description=description,
        section=section,
        content=content,
        url=url,
        source=source,
    )


def test_database_initialisation() -> None:
    """Test database initialisation creates schema."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)
        assert db.db_path == db_path
        assert db_path.exists()


def test_upsert_document() -> None:
    """Test inserting and updating a document."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc = _make_doc(
            path="a2a/topics/key-concepts.md",
            title="Core Concepts",
            description="Core concepts of the A2A protocol",
            content="Content about A2A core concepts",
            url="https://a2a-protocol.org/latest/topics/key-concepts/",
        )

        db.upsert_document(doc)
        retrieved = db.get_document("a2a/topics/key-concepts.md")

        assert retrieved is not None
        assert retrieved.title == "Core Concepts"
        assert retrieved.content == "Content about A2A core concepts"
        assert retrieved.source == "a2a"


def test_upsert_document_update() -> None:
    """Test updating an existing document."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc1 = _make_doc(
            path="a2a/topics/key-concepts.md",
            title="Original",
            content="Original content",
        )
        db.upsert_document(doc1)

        doc2 = _make_doc(
            path="a2a/topics/key-concepts.md",
            title="Updated",
            content="Updated content",
        )
        db.upsert_document(doc2)

        retrieved = db.get_document("a2a/topics/key-concepts.md")
        assert retrieved is not None
        assert retrieved.title == "Updated"
        assert retrieved.content == "Updated content"


def test_search_documents() -> None:
    """Test searching documents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc1 = _make_doc(
            path="a2a/doc1.md",
            title="Agent Discovery",
            description="How agents discover each other",
            content="This document covers A2A agent discovery via Agent Cards",
        )
        doc2 = _make_doc(
            path="a2a/doc2.md",
            title="Streaming and Async",
            description="Streaming guide",
            content="This document covers A2A streaming and asynchronous operations",
        )

        db.upsert_document(doc1)
        db.upsert_document(doc2)

        results = db.search("discovery")
        assert len(results) > 0
        assert any("Discovery" in r.title for r in results)


def test_search_with_section_filter() -> None:
    """Test searching with section filter."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc1 = _make_doc(
            path="a2a/topics/doc1.md",
            title="A2A Concepts",
            section="topics",
            content="Concept documentation",
        )
        doc2 = _make_doc(
            path="a2a/tutorials/doc2.md",
            title="A2A Tutorial",
            section="tutorials",
            content="Tutorial about A2A",
            url="https://a2a-protocol.org/latest/tutorials/",
        )

        db.upsert_document(doc1)
        db.upsert_document(doc2)

        results = db.search("A2A", section="topics")
        assert len(results) == 1
        assert results[0].section == "topics"


def test_search_with_source_filter() -> None:
    """Test searching with source filter."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc1 = _make_doc(
            path="a2a/topics/overview.md",
            title="A2A Overview",
            content="A2A is an agent interoperability protocol",
            source="a2a",
        )

        db.upsert_document(doc1)

        results = db.search("A2A", source="a2a")
        assert len(results) == 1
        assert results[0].source == "a2a"

        no_results = db.search("A2A", source="other")
        assert len(no_results) == 0


def test_search_with_malformed_query_returns_empty_list() -> None:
    """Test that a syntactically invalid FTS5 query is handled gracefully."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc = _make_doc(path="a2a/topics/overview.md", content="A2A overview")
        db.upsert_document(doc)

        results = db.search('"unclosed quote')
        assert results == []


def test_get_document_not_found() -> None:
    """Test getting a non-existent document."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        result = db.get_document("nonexistent.md")
        assert result is None


def test_clear_database() -> None:
    """Test clearing all documents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc = _make_doc(path="a2a/test.md")
        db.upsert_document(doc)

        assert db.get_document_count() == 1

        db.clear()

        assert db.get_document_count() == 0


def test_get_document_count() -> None:
    """Test getting document count."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        assert db.get_document_count() == 0

        for i in range(5):
            doc = _make_doc(
                path=f"a2a/doc{i}.md",
                title=f"Doc {i}",
                content=f"Content {i}",
            )
            db.upsert_document(doc)

        assert db.get_document_count() == 5
