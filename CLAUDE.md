# Claude Code Instructions

This file contains instructions for Claude Code when working with the MCP A2A Documentation Server codebase.

## Project Overview

This is an MCP (Model Context Protocol) server that provides search and retrieval tools for Agent2Agent (A2A) protocol documentation. It uses:

- FastMCP for the MCP server framework
- SQLite FTS5 for full-text search with BM25 ranking
- Python-frontmatter for parsing markdown files with YAML frontmatter
- Sparse Git checkout for efficient cloning of the documentation directory
- One upstream source:
  - [`a2aproject/A2A`](https://github.com/a2aproject/A2A) — the `docs/` directory, which powers [a2a-protocol.org](https://a2a-protocol.org)

## Code Principles

### British English
- Use British English in all code, comments, and documentation
- Examples: "initialise" not "initialize", "colour" not "color"

### Type Safety
- All functions must have type hints
- Use modern union syntax: `str | None` instead of `Optional[str]`
- Run mypy in strict mode before committing

### Error Handling
- Use explicit error handling
- Raise appropriate exceptions with descriptive messages
- Never silently fail

### Code Style
- Follow PEP 8 guidelines
- Maximum line length: 120 characters
- Use ruff for linting and formatting
- See CODESTYLE.md for detailed style guidelines

## Development Workflow

### Making Changes

1. **Before starting**:
   - Ensure development environment is initialised: `make init`
   - Understand the existing code structure

2. **During development**:
   - Write tests for new functionality
   - Update type hints as needed
   - Add docstrings following Google style

3. **Before committing**:
   - Format code: `make format`
   - Run linter: `make lint`
   - Run type checker: `make typecheck`
   - Run tests: `make test`
   - Or run all checks: `make build`

### Testing

- Write tests using pytest
- Place tests in `tests/` directory
- Mirror source structure in test files
- Test both success and failure cases
- Aim for high coverage (>80%)

### Common Tasks

#### Adding a New Feature

1. Update the relevant model in `models.py` if needed
2. Implement the feature in the appropriate module
3. Add corresponding tests
4. Update documentation
5. Run `make build` to verify all checks pass

#### Modifying the Parser

When modifying `parser.py`:
- The site is served with [mike](https://github.com/jimporter/mike) versioning, so all
  published URLs are prefixed with `/latest/` (`A2A_DOCS_BASE_URL`)
- Update URL computation if the upstream mkdocs URL scheme changes
- Standard mkdocs convention: `page.md` -> `/page/`, `dir/index.md` -> `/dir/`
- No Hugo shortcodes or blog date patterns are used by this source (unlike some sibling
  documentation servers) — only HTML comments/tags need stripping

#### Updating Dependencies

1. Modify `pyproject.toml`
2. Run `make generate` to update lock file
3. Test thoroughly
4. Document the reason for the dependency

#### Indexer Modifications

When modifying `indexer.py`:
- Consider network efficiency (sparse checkout of `docs/` only)
- Handle Git operations safely
- Log progress appropriately
- Test with different branches
- The `SOURCES` tuple is designed to allow additional upstream repositories (e.g. a
  future `a2a-samples` source) without restructuring the indexer

## Project Structure

```
mcp-a2a-documentation/
├── src/mcp_a2a_documentation/
│   ├── __init__.py         # Package initialisation
│   ├── models.py           # Data models (Document, SearchResult, etc.)
│   ├── database.py         # SQLite FTS5 database operations
│   ├── parser.py           # Markdown parser
│   ├── indexer.py          # Documentation indexer
│   ├── server.py           # FastMCP server implementation
│   └── cli.py              # Command-line interface
├── tests/                  # Test files
├── data/                   # SQLite database storage
├── pyproject.toml          # Project configuration
├── Makefile                # Build automation
├── Dockerfile              # Container configuration
└── README.md               # Project documentation
```

## MCP Tools

The server exposes two MCP tools:

1. **search_documentation**: Full-text search with optional section and source filtering
2. **read_documentation**: Retrieve complete document content by its source-prefixed path

Both tools return JSON-formatted responses.

## Database Schema

The database has two main tables:
- `documents`: Main document storage (with a `source` column distinguishing upstreams)
- `documents_fts`: FTS5 virtual table for search

Triggers keep the FTS index synchronised with the main table.

## Common Patterns

### Database Operations
Always use the context manager pattern:
```python
with self._get_connection() as conn:
    # Perform operations
    conn.commit()
```

### Lazy Initialisation
The server uses lazy initialisation for the database:
```python
_database: DocumentDatabase | None = None

def get_database() -> DocumentDatabase:
    global _database
    if _database is None:
        _database = DocumentDatabase(db_path)
    return _database
```

### Error Messages
Provide helpful error messages with suggestions:
```python
return json.dumps({
    "error": f"Document not found: {path}",
    "suggestion": "Use search_documentation to find valid document paths.",
})
```

## Debugging

### Index Issues
If the index isn't working correctly:
1. Check index statistics: `uv run a2a-docs-index stats`
2. Rebuild the index: `uv run a2a-docs-index index --rebuild`
3. Check database file permissions
4. Verify Git clone succeeded

### Search Not Finding Results
1. Verify stemming is working (Porter stemmer)
2. Check BM25 scoring weights
3. Examine the FTS5 query syntax
4. Test with simpler queries

### Docker Build Failures
1. Ensure Git is available in the container
2. Check network connectivity during build
3. Verify sparse checkout configuration
4. Check uv installation

## Container Image

The `martoc/mcp-a2a-documentation` container image is published to Docker Hub with the documentation index pre-built.

- **Image**: `martoc/mcp-a2a-documentation`
- **Platforms**: `linux/amd64`, `linux/arm64`
- **CI/CD**: Built and published automatically via GitHub Actions on push to `main`
- **Index**: Pre-built at image build time from the `main` branch of `a2aproject/A2A`

## Documentation URLs

Published URL pattern (mike-versioned mkdocs site):

| Source | Filesystem path | URL pattern |
|--------|-----------------|-------------|
| `a2a` | `<path>.md` (under `docs/`) | `https://a2a-protocol.org/latest/<path>/` |
| `a2a` | `index.md` | `https://a2a-protocol.org/latest/` |
| `a2a` | `<dir>/index.md` | `https://a2a-protocol.org/latest/<dir>/` |

The parser removes `.md` extensions and handles `index.md` pages when computing URLs.

## Git Operations

The indexer uses sparse checkout to clone the upstream source:

```bash
git clone --depth 1 --filter=blob:none --sparse --branch main \
    https://github.com/a2aproject/A2A.git
git sparse-checkout set docs
```

This significantly reduces clone time and disk usage.

## Performance Considerations

- **SQLite FTS5**: Provides fast full-text search with BM25 ranking
- **Sparse checkout**: Reduces clone size by fetching only the `docs/` directory
- **Lazy loading**: Database initialised only when needed
- **Connection pooling**: Not needed for SQLite (file-based)

## Maintenance

### Updating to New Upstream Versions

1. Update the branch in the indexer CLI if needed
2. Rebuild the index: `uv run a2a-docs-index index --rebuild --branch main`
3. Test search functionality
4. Update README with version info

### Monitoring Index Health

Regularly check:
- Document count: `uv run a2a-docs-index stats`
- Search result quality
- Database file size
- Query performance

## Troubleshooting

### Import Errors
- Ensure virtual environment is activated
- Run `make init` to sync dependencies
- Check Python version (requires 3.12+)

### Type Check Failures
- Review mypy output carefully
- Update type hints as needed
- Check for missing return type annotations

### Test Failures
- Review test output for details
- Check test database setup
- Verify fixtures are correct
- Run with verbose output: `pytest -vvv`

## Best Practices

1. **Never** commit without running `make build`
2. **Always** write tests for new features
3. **Keep** functions focused and single-purpose
4. **Use** type hints consistently
5. **Document** non-obvious behaviour
6. **Follow** British English spelling
7. **Update** documentation when changing behaviour
8. **Test** with different upstream branches
