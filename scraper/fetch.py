from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Article:
    url: str
    slug: str
    title: str
    html: str
    source_updated_at: str | None = None


def fetch_articles(base_url: str, limit: int) -> list[Article]:
    """Fetch support articles.

    Implementation comes next: discover article URLs, download article HTML,
    and return normalized article records.
    """
    raise NotImplementedError("Article discovery and fetching are not implemented yet.")

