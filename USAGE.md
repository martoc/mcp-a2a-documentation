# Usage Guide

This guide provides detailed instructions for using the MCP A2A Documentation Server.

## Installation

### Prerequisites

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/) package manager
- Git
- Docker (optional, for containerised deployment)

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/martoc/mcp-a2a-documentation.git
   cd mcp-a2a-documentation
   ```

2. Initialise the development environment:
   ```bash
   make init
   ```

3. Build the documentation index:
   ```bash
   make index
   ```

## Indexing Documentation

### Initial Indexing

Index A2A protocol documentation from the `main` branch of the upstream repository:

```bash
uv run a2a-docs-index index
```

### Rebuilding the Index

Clear the existing index and rebuild from scratch:

```bash
uv run a2a-docs-index index --rebuild
```

### Indexing a Specific Branch

Index documentation from a specific Git branch:

```bash
uv run a2a-docs-index index --branch main
```

### Index Statistics

View the number of indexed documents:

```bash
uv run a2a-docs-index stats
```

## Running the MCP Server

### Using the Container Image (Recommended)

The `martoc/mcp-a2a-documentation` container image is published to Docker Hub with the documentation index pre-built. Available for `linux/amd64` and `linux/arm64`.

```bash
# Pull and run the server
docker run -i --rm martoc/mcp-a2a-documentation:latest
```

### Local Development

Run the server directly using uv:

```bash
make run
# or
uv run mcp-a2a-documentation
```

### Building a Local Docker Image

Build and run the server in a Docker container:

```bash
make docker-build
make docker-run
```

## MCP Client Configuration

### Claude Code (Container Image)

Add to your project's `.mcp.json` to use the published container image:

```json
{
  "mcpServers": {
    "a2a-documentation": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "martoc/mcp-a2a-documentation:latest"]
    }
  }
}
```

### Claude Code (Local Development)

Add to your project's `.mcp.json` for local development:

```json
{
  "mcpServers": {
    "a2a-documentation": {
      "command": "uv",
      "args": ["run", "mcp-a2a-documentation"],
      "cwd": "/path/to/mcp-a2a-documentation"
    }
  }
}
```

### Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "a2a-documentation": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "martoc/mcp-a2a-documentation:latest"]
    }
  }
}
```

## Using the Tools

### Searching Documentation

Search for topics across A2A protocol documentation:

```
Search for "agent card"
Search for "streaming" in section "topics"
Search for "quickstart" in source "a2a"
Search for "extension" with limit 20
```

Example response:

```json
{
  "query": "agent card",
  "section_filter": null,
  "source_filter": null,
  "result_count": 1,
  "results": [
    {
      "title": "Agent Discovery",
      "url": "https://a2a-protocol.org/latest/topics/agent-discovery/",
      "path": "a2a/topics/agent-discovery.md",
      "section": "topics",
      "source": "a2a",
      "snippet": "...A2A standardizes agent self-descriptions through the Agent Card...",
      "relevance_score": 3.1102
    }
  ]
}
```

### Reading Documentation

Retrieve the full content of a specific page:

```
Read documentation at path "a2a/topics/what-is-a2a.md"
Read documentation at path "a2a/specification.md"
```

Example response:

```json
{
  "path": "a2a/topics/what-is-a2a.md",
  "title": "What is A2A?",
  "description": null,
  "section": "topics",
  "source": "a2a",
  "url": "https://a2a-protocol.org/latest/topics/what-is-a2a/",
  "content": "# What is A2A?\n\n..."
}
```

## Sources and Sections

The server indexes a single upstream source:

- **a2a** — files from the `docs/` directory of [`a2aproject/A2A`](https://github.com/a2aproject/A2A), serving [a2a-protocol.org](https://a2a-protocol.org).
  Common sections: `root` (specification, community, roadmap, partners, blog posts), `topics` (core protocol concepts and extensions), `tutorials` (the Python quickstart), `sdk` (SDK overview).

Use the `section` parameter to narrow search results.

## Development Workflow

### Code Quality Checks

Run all code quality checks:

```bash
make build
```

This runs:
- Linter (ruff)
- Type checker (mypy)
- Tests with coverage (pytest)

### Individual Checks

```bash
make lint       # Run linter only
make typecheck  # Run type checker only
make test       # Run tests only
make format     # Format code
```

### Updating Dependencies

Update the lock file:

```bash
make generate
```

## Troubleshooting

### Index Build Fails

If the index build fails, try:

1. Check your internet connection
2. Verify Git is installed and accessible
3. Try rebuilding with a different branch:
   ```bash
   uv run a2a-docs-index index --rebuild --branch main
   ```

### No Search Results

If searches return no results:

1. Verify the index is built:
   ```bash
   uv run a2a-docs-index stats
   ```

2. Rebuild the index if necessary:
   ```bash
   uv run a2a-docs-index index --rebuild
   ```

### Database Location

The default database location is `data/a2a_docs.db`. To use a custom location:

```bash
uv run a2a-docs-index index --database /path/to/custom.db
```

## Performance Considerations

- **Initial indexing**: Typically completes in a few seconds given the small size of the `docs/` directory
- **Sparse checkout**: Only the `docs/` directory of `a2aproject/A2A` is fetched
- **Search performance**: FTS5 with BM25 ranking provides fast, relevant results
- **Memory usage**: Minimal during operation; database is SQLite-based
