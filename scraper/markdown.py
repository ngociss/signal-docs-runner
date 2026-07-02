from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scraper.fetch import Article


MARKDOWN_DIR = Path("data/markdown")


@dataclass(frozen=True)
class MarkdownArticle:
    url: str
    slug: str
    title: str
    path: Path
    content_hash: str
    source_updated_at: str | None = None


def write_markdown_files(articles: list[Article]) -> list[MarkdownArticle]:
    """Convert fetched articles to clean Markdown files."""
    raise NotImplementedError("Markdown conversion is not implemented yet.")

