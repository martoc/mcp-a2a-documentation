"""Tests for document parser."""

import tempfile
from pathlib import Path

from mcp_a2a_documentation.parser import DocumentParser


def test_extract_section_root() -> None:
    """Test extracting section from root-level file."""
    parser = DocumentParser()
    section = parser._extract_section(Path("index.md"))
    assert section == "root"


def test_extract_section_nested() -> None:
    """Test extracting section from nested file."""
    parser = DocumentParser()
    section = parser._extract_section(Path("topics/what-is-a2a.md"))
    assert section == "topics"


def test_compute_a2a_url_root_index() -> None:
    """Test computing URL for the root index page."""
    parser = DocumentParser()
    url = parser._compute_url(Path("index.md"), DocumentParser.SOURCE_A2A)
    assert url == "https://a2a-protocol.org/latest/"


def test_compute_a2a_url_root_page() -> None:
    """Test computing URL for a top-level docs page."""
    parser = DocumentParser()
    url = parser._compute_url(Path("specification.md"), DocumentParser.SOURCE_A2A)
    assert url == "https://a2a-protocol.org/latest/specification/"


def test_compute_a2a_url_nested_page() -> None:
    """Test computing URL for a nested topics page."""
    parser = DocumentParser()
    url = parser._compute_url(Path("topics/what-is-a2a.md"), DocumentParser.SOURCE_A2A)
    assert url == "https://a2a-protocol.org/latest/topics/what-is-a2a/"


def test_compute_a2a_url_nested_index() -> None:
    """Test computing URL for a nested index page."""
    parser = DocumentParser()
    url = parser._compute_url(Path("tutorials/index.md"), DocumentParser.SOURCE_A2A)
    assert url == "https://a2a-protocol.org/latest/tutorials/"


def test_compute_a2a_url_deeply_nested_page() -> None:
    """Test computing URL for a deeply nested tutorial page."""
    parser = DocumentParser()
    url = parser._compute_url(
        Path("tutorials/python/1-introduction.md"),
        DocumentParser.SOURCE_A2A,
    )
    assert url == "https://a2a-protocol.org/latest/tutorials/python/1-introduction/"


def test_compute_url_unknown_source() -> None:
    """Test computing URL for an unrecognised source returns an empty string."""
    parser = DocumentParser()
    url = parser._compute_url(Path("topics/what-is-a2a.md"), "unknown")
    assert url == ""


def test_clean_content_removes_html_comments() -> None:
    """Test cleaning content removes HTML comments."""
    parser = DocumentParser()
    content = "<!-- markdownlint-disable MD041 -->\nContent\n<!-- Another -->"
    cleaned = parser._clean_content(content)
    assert "<!--" not in cleaned
    assert "Content" in cleaned


def test_clean_content_removes_html_tags() -> None:
    """Test cleaning content removes raw HTML tags."""
    parser = DocumentParser()
    content = '<div style="text-align: center;" markdown>\nContent\n</div>'
    cleaned = parser._clean_content(content)
    assert "<div" not in cleaned
    assert "Content" in cleaned


def test_parse_file_with_frontmatter() -> None:
    """Test parsing a file with YAML frontmatter."""
    parser = DocumentParser()

    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        file_path = base_path / "topics" / "what-is-a2a.md"
        file_path.parent.mkdir(parents=True)

        content = """---
title: What is A2A?
description: An introduction to the A2A protocol.
---

## What is A2A Protocol?

The A2A protocol is an open standard for agent interoperability.
"""
        file_path.write_text(content)

        doc = parser.parse_file(file_path, base_path, DocumentParser.SOURCE_A2A)

        assert doc is not None
        assert doc.title == "What is A2A?"
        assert doc.description == "An introduction to the A2A protocol."
        assert "A2A protocol" in doc.content
        assert doc.path == "a2a/topics/what-is-a2a.md"
        assert doc.section == "topics"
        assert doc.source == "a2a"
        assert doc.url == "https://a2a-protocol.org/latest/topics/what-is-a2a/"


def test_parse_file_without_frontmatter_title() -> None:
    """Test parsing a file without a title in frontmatter falls back to the filename."""
    parser = DocumentParser()

    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        file_path = base_path / "what-is-a2a.md"

        content = "# What is A2A?\n\nThis is a test."
        file_path.write_text(content)

        doc = parser.parse_file(file_path, base_path, DocumentParser.SOURCE_A2A)

        assert doc is not None
        assert doc.title == "What Is A2A"  # Fallback from filename
        assert "This is a test." in doc.content
        assert doc.section == "root"
