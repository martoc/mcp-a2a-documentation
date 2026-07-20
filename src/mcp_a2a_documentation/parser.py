"""Parser for A2A protocol documentation markdown files."""

import re
from pathlib import Path

import frontmatter

from mcp_a2a_documentation.models import Document, DocumentMetadata


class DocumentParser:
    """Parses markdown files with YAML frontmatter."""

    # The site is served with mike versioning; "latest" is the alias mike
    # points at the most recent released version.
    A2A_DOCS_BASE_URL = "https://a2a-protocol.org/latest"

    SOURCE_A2A = "a2a"

    def parse_file(self, file_path: Path, base_path: Path, source: str) -> Document | None:
        """Parse a markdown file and extract metadata and content.

        Args:
            file_path: Path to the markdown file.
            base_path: Base path of the documentation directory.
            source: Source identifier for the upstream repository.

        Returns:
            Document instance or None if parsing fails.
        """
        try:
            post = frontmatter.load(file_path)
            metadata = self._extract_metadata(post.metadata, file_path)
            relative_path = file_path.relative_to(base_path)
            section = self._extract_section(relative_path)
            url = self._compute_url(relative_path, source)
            content = self._clean_content(post.content)

            prefixed_path = f"{source}/{relative_path}"

            return Document(
                path=prefixed_path,
                title=metadata.title,
                description=metadata.description,
                section=section,
                content=content,
                url=url,
                source=source,
            )
        except Exception:
            return None

    def _extract_metadata(self, metadata: dict[str, object], file_path: Path) -> DocumentMetadata:
        """Extract structured metadata from frontmatter.

        Args:
            metadata: Dictionary of frontmatter fields.
            file_path: Path to the file for fallback title extraction.

        Returns:
            DocumentMetadata instance.
        """
        title = metadata.get("title")
        if not isinstance(title, str):
            title = file_path.stem.replace("-", " ").replace("_", " ").title()

        description = metadata.get("description")
        if not isinstance(description, str):
            description = None

        return DocumentMetadata(
            title=title,
            description=description,
        )

    def _extract_section(self, relative_path: Path) -> str:
        """Extract the top-level section from the path.

        Args:
            relative_path: Path relative to docs directory.

        Returns:
            Section name (first directory component or 'root').
        """
        parts = relative_path.parts
        return parts[0] if len(parts) > 1 else "root"

    def _compute_url(self, relative_path: Path, source: str) -> str:
        """Compute the documentation URL for the given source.

        Args:
            relative_path: Path relative to the documentation base directory.
            source: Source identifier (a2a).

        Returns:
            Full URL to the documentation page.
        """
        if source == self.SOURCE_A2A:
            return self._compute_a2a_url(relative_path)
        return ""

    def _compute_a2a_url(self, relative_path: Path) -> str:
        """Compute the a2a-protocol.org URL for a docs page.

        Follows the standard mkdocs URL convention: `page.md` maps to
        `/page/` and `dir/index.md` maps to `/dir/`.

        Args:
            relative_path: Path relative to the a2aproject/A2A `docs/` directory.

        Returns:
            Full URL on a2a-protocol.org.
        """
        base = self.A2A_DOCS_BASE_URL
        path_str = re.sub(r"\.md$", "", str(relative_path))

        if path_str == "index":
            return f"{base}/"

        path_str = re.sub(r"/index$", "/", path_str)
        if path_str.endswith("/"):
            return f"{base}/{path_str}"
        return f"{base}/{path_str}/"

    def _clean_content(self, content: str) -> str:
        """Clean markdown content for indexing.

        Removes HTML comments and tags left over from mkdocs-material markup.

        Args:
            content: Raw markdown content.

        Returns:
            Cleaned content suitable for indexing.
        """
        # Remove HTML comments
        content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
        # Remove HTML tags
        content = re.sub(r"<[^>]+>", "", content)
        return content.strip()
