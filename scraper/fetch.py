from __future__ import annotations

from dataclasses import dataclass
import re
from urllib.parse import urljoin

import httpx


@dataclass(frozen=True)
class Article:
    url: str
    slug: str
    title: str
    html: str
    source_updated_at: str | None = None


def _slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def _slug_from_article(article: dict) -> str:
    html_url = article.get("html_url") or ""
    match = re.search(r"/articles/\d+-(?P<slug>[^/?#]+)", html_url)
    if match:
        return _slugify(match.group("slug"))

    title = article.get("title") or str(article["id"])
    return _slugify(title)


def fetch_articles(base_url: str, limit: int) -> list[Article]:
    """Fetch support articles from the Zendesk Help Center API."""
    if limit < 1:
        return []

    articles_api_url = urljoin(
        base_url.rstrip("/") + "/",
        "api/v2/help_center/en-us/articles.json?per_page=100",
    )
    youtube_api_url = urljoin(
        base_url.rstrip("/") + "/",
        "api/v2/help_center/articles/search.json?query=YouTube&per_page=30",
    )
    articles: list[Article] = []
    seen_urls: set[str] = set()

    with httpx.Client(
        timeout=30,
        follow_redirects=True,
        headers={"User-Agent": "signal-docs-runner/0.1"},
    ) as client:
        _collect_articles(client, youtube_api_url, articles, seen_urls, limit)

        next_page: str | None = articles_api_url

        while next_page and len(articles) < limit:
            response = client.get(next_page)
            response.raise_for_status()
            payload = response.json()

            for item in payload.get("articles", []):
                if _append_article(item, articles, seen_urls):
                    if len(articles) >= limit:
                        break

            next_page = payload.get("next_page")

    return articles[:limit]


def _collect_articles(
    client: httpx.Client,
    api_url: str,
    articles: list[Article],
    seen_urls: set[str],
    limit: int,
) -> None:
    next_page: str | None = api_url

    while next_page and len(articles) < limit:
        response = client.get(next_page)
        response.raise_for_status()
        payload = response.json()

        for item in payload.get("results", []):
            if _append_article(item, articles, seen_urls):
                if len(articles) >= limit:
                    break

        next_page = payload.get("next_page")


def _append_article(
    item: dict,
    articles: list[Article],
    seen_urls: set[str],
) -> bool:
    body = item.get("body") or ""
    html_url = item.get("html_url") or ""
    title = item.get("title") or ""

    if not body or not html_url or not title or html_url in seen_urls:
        return False

    seen_urls.add(html_url)
    articles.append(
        Article(
            url=html_url,
            slug=_slug_from_article(item),
            title=title,
            html=body,
            source_updated_at=item.get("edited_at") or item.get("updated_at"),
        )
    )
    return True
