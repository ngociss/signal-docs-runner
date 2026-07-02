from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from pathlib import Path

from bs4 import BeautifulSoup
from markdownify import markdownify as md

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
    MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)
    expected_paths = {MARKDOWN_DIR / f"{article.slug}.md" for article in articles}

    markdown_articles: list[MarkdownArticle] = []
    for article in articles:
        body = _html_to_markdown(article.html)
        content = _format_article(article, body)
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        path = MARKDOWN_DIR / f"{article.slug}.md"
        path.write_text(content, encoding="utf-8")

        markdown_articles.append(
            MarkdownArticle(
                url=article.url,
                slug=article.slug,
                title=article.title,
                path=path,
                content_hash=content_hash,
                source_updated_at=article.source_updated_at,
            )
        )

    for stale_path in MARKDOWN_DIR.glob("*.md"):
        if stale_path not in expected_paths:
            stale_path.unlink()

    return markdown_articles


def _html_to_markdown(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(True):
        tag.attrs = _clean_attrs(tag.name, tag.attrs)

    markdown = md(
        str(soup),
        heading_style="ATX",
        bullets="-",
        strip=["script", "style"],
    )
    markdown = re.sub(r"(!\[[^\]]*\]\([^)]+\))(?=\S)", r"\1\n\n", markdown)
    markdown = markdown.replace("\xa0", " ")
    lines = [line.rstrip() for line in markdown.splitlines()]
    compacted: list[str] = []
    blank_count = 0

    for line in lines:
        if line.strip():
            blank_count = 0
            compacted.append(line)
        else:
            blank_count += 1
            if blank_count <= 1:
                compacted.append("")

    return "\n".join(compacted).strip()


def _clean_attrs(tag_name: str, attrs: dict) -> dict:
    keep: dict = {}

    if tag_name == "a":
        href = attrs.get("href")
        if href:
            keep["href"] = href

    if tag_name == "img":
        src = attrs.get("src")
        alt = attrs.get("alt")
        if src:
            keep["src"] = src
        if alt:
            keep["alt"] = alt

    if tag_name in {"code", "pre"}:
        class_name = attrs.get("class")
        if class_name:
            keep["class"] = class_name

    return keep


def _format_article(article: Article, body: str) -> str:
    source_updated_at = article.source_updated_at or ""
    return (
        "---\n"
        f'title: "{_escape_yaml(article.title)}"\n'
        f'article_url: "{article.url}"\n'
        f'source_updated_at: "{source_updated_at}"\n'
        "---\n\n"
        f"# {article.title}\n\n"
        f"Article URL: {article.url}\n\n"
        f"{body}\n"
    )


def _escape_yaml(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
