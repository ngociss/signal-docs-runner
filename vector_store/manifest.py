from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any

from scraper.markdown import MarkdownArticle


MANIFEST_PATH = Path("data/manifest.json")
UPLOAD_PROVIDER = "gemini-file-search"


@dataclass(frozen=True)
class ArticleChanges:
    added: list[MarkdownArticle]
    updated: list[MarkdownArticle]
    skipped: list[MarkdownArticle]


def load_manifest() -> dict[str, dict[str, Any]]:
    """Load previous article upload state."""
    if not MANIFEST_PATH.exists():
        return {}

    with MANIFEST_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def diff_articles(
    articles: list[MarkdownArticle],
    manifest: dict[str, dict[str, Any]],
) -> ArticleChanges:
    """Classify articles as added, updated, or skipped."""
    added: list[MarkdownArticle] = []
    updated: list[MarkdownArticle] = []
    skipped: list[MarkdownArticle] = []
    gemini_configured = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))

    for article in articles:
        current = manifest.get(article.url)
        if current is None:
            added.append(article)
        elif current.get("content_hash") != article.content_hash:
            updated.append(article)
        elif gemini_configured and (
            current.get("upload_provider") != UPLOAD_PROVIDER
            or not current.get("uploaded_file_id")
        ):
            updated.append(article)
        else:
            skipped.append(article)

    return ArticleChanges(added=added, updated=updated, skipped=skipped)


def save_manifest(
    manifest: dict[str, dict[str, Any]],
    changes: ArticleChanges,
    upload_result: Any,
) -> None:
    """Persist article upload state after a successful run."""
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_ids_by_url = getattr(upload_result, "file_ids_by_url", {})

    for article in changes.added + changes.updated + changes.skipped:
        existing = manifest.get(article.url, {})
        uploaded_file_id = file_ids_by_url.get(article.url, existing.get("uploaded_file_id"))
        manifest[article.url] = {
            "slug": article.slug,
            "title": article.title,
            "path": article.path.as_posix(),
            "content_hash": article.content_hash,
            "source_updated_at": article.source_updated_at,
            "uploaded_file_id": uploaded_file_id,
            "upload_provider": UPLOAD_PROVIDER,
        }

    current_urls = {article.url for article in changes.added + changes.updated + changes.skipped}
    stale_urls = set(manifest) - current_urls
    for url in stale_urls:
        del manifest[url]

    with MANIFEST_PATH.open("w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2, sort_keys=True)
        file.write("\n")
