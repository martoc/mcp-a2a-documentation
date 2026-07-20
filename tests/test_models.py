"""Tests for data models."""

from mcp_a2a_documentation.models import Document, DocumentMetadata, SearchResult


def test_document_metadata_creation() -> None:
    """Test creating a DocumentMetadata instance."""
    metadata = DocumentMetadata(
        title="What is A2A?",
        description="Introduction to the A2A protocol",
    )
    assert metadata.title == "What is A2A?"
    assert metadata.description == "Introduction to the A2A protocol"


def test_document_metadata_optional_fields() -> None:
    """Test DocumentMetadata with optional fields."""
    metadata = DocumentMetadata(title="Overview")
    assert metadata.title == "Overview"
    assert metadata.description is None


def test_document_creation() -> None:
    """Test creating a Document instance."""
    doc = Document(
        path="a2a/topics/what-is-a2a.md",
        title="What is A2A?",
        description="Introduction to the A2A protocol",
        section="topics",
        content="# What is A2A?\n\nContent here",
        url="https://a2a-protocol.org/latest/topics/what-is-a2a/",
        source="a2a",
    )
    assert doc.path == "a2a/topics/what-is-a2a.md"
    assert doc.title == "What is A2A?"
    assert doc.section == "topics"
    assert doc.source == "a2a"
    assert "Content here" in doc.content


def test_search_result_creation() -> None:
    """Test creating a SearchResult instance."""
    result = SearchResult(
        path="a2a/topics/what-is-a2a.md",
        title="What is A2A?",
        url="https://a2a-protocol.org/latest/topics/what-is-a2a/",
        snippet="...A2A protocol enables communication...",
        score=12.5,
        section="topics",
        source="a2a",
    )
    assert result.path == "a2a/topics/what-is-a2a.md"
    assert result.score == 12.5
    assert result.section == "topics"
    assert result.source == "a2a"
