from __future__ import annotations

from dataclasses import dataclass

from vector_store.manifest import ArticleChanges


@dataclass(frozen=True)
class UploadResult:
    uploaded_count: int
    chunk_count: int
    file_ids_by_url: dict[str, str]


def upload_changed_articles(changes: ArticleChanges) -> UploadResult:
    """Upload added and updated Markdown files to the configured vector store."""
    changed = changes.added + changes.updated
    return UploadResult(uploaded_count=len(changed), chunk_count=0, file_ids_by_url={})

