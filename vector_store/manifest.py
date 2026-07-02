from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scraper.markdown import MarkdownArticle


MANIFEST_PATH = Path("data/manifest.json")


@dataclass(frozen=True)
class ArticleChanges:
    added: list[MarkdownArticle]
    updated: list[MarkdownArticle]
    skipped: list[MarkdownArticle]


def load_manifest() -> dict:
    """Load previous article upload state."""
    return {}


def diff_articles(articles: list[MarkdownArticle], manifest: dict) -> ArticleChanges:
    """Classify articles as added, updated, or skipped."""
    return ArticleChanges(added=articles, updated=[], skipped=[])


def save_manifest(manifest: dict, changes: ArticleChanges, upload_result: object) -> None:
    """Persist article upload state after a successful run."""
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

