"""Tests for the documentation indexer (excluding network operations)."""

import tempfile
from pathlib import Path

import pytest

from mcp_a2a_documentation.database import DocumentDatabase
from mcp_a2a_documentation.indexer import A2ADocsIndexer


def _make_indexer() -> A2ADocsIndexer:
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"
    database = DocumentDatabase(db_path)
    return A2ADocsIndexer(database)


def test_find_source_known() -> None:
    """Test finding a known documentation source by name."""
    indexer = _make_indexer()
    source = indexer._find_source("a2a")
    assert source.name == "a2a"
    assert source.repo_url == "https://github.com/a2aproject/A2A.git"
    assert source.content_subpath == "docs"


def test_find_source_unknown_raises() -> None:
    """Test finding an unknown documentation source raises ValueError."""
    indexer = _make_indexer()
    with pytest.raises(ValueError, match="Unknown documentation source"):
        indexer._find_source("unknown")


def test_should_index_excludes_readme() -> None:
    """Test that README.md is excluded from indexing."""
    indexer = _make_indexer()
    assert indexer._should_index(Path("/tmp/docs/README.md")) is False  # noqa: S108


def test_should_index_includes_regular_page() -> None:
    """Test that a regular documentation page is included."""
    indexer = _make_indexer()
    assert indexer._should_index(Path("/tmp/docs/topics/what-is-a2a.md")) is True  # noqa: S108


def test_index_from_path_missing_directory_raises() -> None:
    """Test indexing from a non-existent path raises ValueError."""
    indexer = _make_indexer()
    with tempfile.TemporaryDirectory() as temp_dir:
        missing_path = Path(temp_dir) / "does-not-exist"
        with pytest.raises(ValueError, match="Content path does not exist"):
            indexer.index_from_path("a2a", missing_path)


def test_index_from_path_indexes_markdown_files() -> None:
    """Test indexing markdown files from a local path."""
    indexer = _make_indexer()
    with tempfile.TemporaryDirectory() as temp_dir:
        docs_path = Path(temp_dir) / "docs"
        topics_path = docs_path / "topics"
        topics_path.mkdir(parents=True)

        (docs_path / "index.md").write_text("# Home\n\nWelcome to A2A.")
        (docs_path / "README.md").write_text("# Repo readme, should be excluded")
        (topics_path / "what-is-a2a.md").write_text("# What is A2A?\n\nAn open protocol.")

        count = indexer.index_from_path("a2a", Path(temp_dir))

        assert count == 2
        assert indexer.database.get_document_count() == 2
        assert indexer.database.get_document("a2a/index.md") is not None
        assert indexer.database.get_document("a2a/topics/what-is-a2a.md") is not None
