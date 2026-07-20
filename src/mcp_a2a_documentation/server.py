"""FastMCP server for A2A protocol documentation search and retrieval."""

import json
import logging
from pathlib import Path

from fastmcp import FastMCP

from mcp_a2a_documentation.database import DocumentDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default database path
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "a2a_docs.db"

# Initialise FastMCP server
mcp = FastMCP(name="a2a-documentation")

# Lazy database initialisation
_database: DocumentDatabase | None = None


def get_database() -> DocumentDatabase:
    """Get or initialise the database instance.

    Returns:
        DocumentDatabase instance.
    """
    global _database
    if _database is None:
        db_path = Path(DEFAULT_DB_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        _database = DocumentDatabase(db_path)
    return _database


def _search_documentation_impl(
    query: str,
    section: str | None = None,
    source: str | None = None,
    limit: int = 10,
) -> str:
    """Core implementation of search_documentation.

    Args:
        query: Search terms to find in the documentation.
        section: Optional section to filter results.
        source: Optional source to filter results ('a2a').
        limit: Maximum number of results to return.

    Returns:
        JSON-formatted search results.
    """
    db = get_database()

    limit = min(max(1, limit), 50)

    results = db.search(query, section=section, source=source, limit=limit)

    if not results:
        return json.dumps(
            {
                "message": f"No results found for query: '{query}'",
                "results": [],
            }
        )

    output = {
        "query": query,
        "section_filter": section,
        "source_filter": source,
        "result_count": len(results),
        "results": [
            {
                "title": r.title,
                "url": r.url,
                "path": r.path,
                "section": r.section,
                "source": r.source,
                "snippet": r.snippet,
                "relevance_score": round(r.score, 4),
            }
            for r in results
        ],
    }

    return json.dumps(output, indent=2)


def _read_documentation_impl(path: str) -> str:
    """Core implementation of read_documentation.

    Args:
        path: The relative path to the documentation file.

    Returns:
        JSON-formatted document content or error message.
    """
    db = get_database()
    document = db.get_document(path)

    if not document:
        return json.dumps(
            {
                "error": f"Document not found: {path}",
                "suggestion": "Use search_documentation to find valid document paths.",
            }
        )

    return json.dumps(
        {
            "path": document.path,
            "title": document.title,
            "description": document.description,
            "section": document.section,
            "source": document.source,
            "url": document.url,
            "content": document.content,
        },
        indent=2,
    )


@mcp.tool()
def search_documentation(
    query: str,
    section: str | None = None,
    source: str | None = None,
    limit: int = 10,
) -> str:
    """Search A2A (Agent2Agent) protocol documentation by keyword query.

    Args:
        query: Search terms to find in the documentation. Supports
               full-text search with stemming (e.g., "authenticate" matches
               "authentication", "authenticated").
        section: Optional section to filter results. Common sections
                 include 'root' (top-level pages such as the specification
                 and community pages), 'topics' (core concepts), 'tutorials',
                 and 'sdk'.
        source: Optional documentation source to filter results. Currently
                only 'a2a' (a2aproject/A2A `docs/` directory) is indexed.
        limit: Maximum number of results to return (default: 10, max: 50).

    Returns:
        JSON-formatted search results with title, URL, snippet, and relevance score.
    """
    return _search_documentation_impl(query, section, source, limit)


@mcp.tool()
def read_documentation(path: str) -> str:
    """Read the full content of a specific A2A protocol documentation page.

    Args:
        path: The relative path to the documentation file, prefixed with the
              source name (e.g., 'a2a/topics/what-is-a2a.md' or
              'a2a/specification.md'). This path is returned in search results.

    Returns:
        The full markdown content of the documentation page, or an error
        message if the page is not found.
    """
    return _read_documentation_impl(path)


def run_server() -> None:
    """Run the MCP server with STDIO transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()
