[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-green.svg)](https://modelcontextprotocol.io/)

# MCP A2A Documentation Server

An MCP (Model Context Protocol) server that provides search and retrieval tools for the [Agent2Agent (A2A) protocol](https://a2a-protocol.org) documentation. This server enables AI assistants like Claude to search and read A2A documentation directly from the upstream repository.

## Source

This server indexes documentation from the [`a2aproject/A2A`](https://github.com/a2aproject/A2A) repository's `docs/` directory, which powers [a2a-protocol.org](https://a2a-protocol.org).

## Features

- **Full-text search** using SQLite FTS5 with BM25 ranking and Porter stemming
- **Section filtering** to narrow search results by documentation category (`root`, `topics`, `tutorials`, `sdk`)
- **Sparse checkout** for efficient cloning of only the required `docs/` directory
- **Docker support** for portable deployment across projects
- **STDIO transport** for seamless MCP client integration

## Quick Start

### Using the Container Image (Recommended)

The `martoc/mcp-a2a-documentation` container image is published to Docker Hub with the documentation index pre-built. Available for `linux/amd64` and `linux/arm64`.

```bash
# Pull and run the server
docker run -i --rm martoc/mcp-a2a-documentation:latest
```

### Building Locally with Docker

```bash
# Build the Docker image (includes pre-indexed documentation)
make docker-build

# Test the server
make docker-run
```

### Using uv (Local Development)

```bash
# Initialise the environment
make init

# Build the documentation index
make index

# Run the server
make run
```

## Container Image

The `martoc/mcp-a2a-documentation` container image is published to [Docker Hub](https://hub.docker.com/r/martoc/mcp-a2a-documentation). It includes the pre-built documentation index so the server is ready to use immediately.

| Property | Value |
|----------|-------|
| Registry | Docker Hub |
| Image | `martoc/mcp-a2a-documentation` |
| Platforms | `linux/amd64`, `linux/arm64` |
| Base image | `python:3.12-slim` |
| Index | Pre-built at image build time from the `main` branch of `a2aproject/A2A` |

```bash
# Pull the latest image
docker pull martoc/mcp-a2a-documentation:latest

# Run the MCP server
docker run -i --rm martoc/mcp-a2a-documentation:latest
```

## Configuration

### Claude Code / Claude Desktop

Add to your `.mcp.json` or global settings to use the published container image:

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

For local development without Docker:

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

## MCP Tools

| Tool | Description |
|------|-------------|
| `search_documentation` | Search A2A documentation by keyword query with optional section filter |
| `read_documentation` | Retrieve the full content of a specific documentation page |

### search_documentation

Search A2A protocol documentation using full-text search with stemming support.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search terms (supports stemming) |
| `section` | string | No | None | Filter by section (`root`, `topics`, `tutorials`, `sdk`) |
| `source` | string | No | None | Filter by source (`a2a`) |
| `limit` | integer | No | 10 | Maximum results (1-50) |

**Available sections:** `root` (specification, community, roadmap, partners, etc.), `topics` (core protocol concepts), `tutorials` (the Python quickstart), `sdk` (SDK overview).

### read_documentation

Retrieve the full content of a documentation page.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Source-prefixed path to the document (e.g., `a2a/topics/what-is-a2a.md`). This path is returned by `search_documentation`. |

## CLI Commands

```bash
# Build/rebuild the documentation index
uv run a2a-docs-index index
uv run a2a-docs-index index --rebuild
uv run a2a-docs-index index --branch main

# Show index statistics
uv run a2a-docs-index stats
```

## Development

```bash
make init       # Initialise development environment
make build      # Run full build (lint, typecheck, test)
make test       # Run tests with coverage
make format     # Format code
make lint       # Run linter
make typecheck  # Run type checker
```

## Documentation

- [USAGE.md](USAGE.md) - Detailed usage instructions
- [CODESTYLE.md](CODESTYLE.md) - Code style guidelines
- [CLAUDE.md](CLAUDE.md) - Claude Code instructions

## Licence

This project is licensed under the MIT Licence - see the [LICENSE](LICENSE) file for details.
