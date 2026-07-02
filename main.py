from __future__ import annotations

import os

from dotenv import load_dotenv

from scraper.fetch import fetch_articles
from scraper.markdown import write_markdown_files
from vector_store.manifest import diff_articles, load_manifest, save_manifest
from vector_store.upload import upload_changed_articles


def main() -> int:
    load_dotenv()

    article_limit = int(os.getenv("ARTICLE_LIMIT", "30"))
    support_base_url = os.getenv("SUPPORT_BASE_URL", "https://support.optisigns.com")

    articles = fetch_articles(base_url=support_base_url, limit=article_limit)
    markdown_articles = write_markdown_files(articles)

    manifest = load_manifest()
    changes = diff_articles(markdown_articles, manifest)
    upload_result = upload_changed_articles(changes)
    save_manifest(manifest, changes, upload_result)

    print(
        "Run complete: "
        f"added={len(changes.added)} "
        f"updated={len(changes.updated)} "
        f"skipped={len(changes.skipped)} "
        f"uploaded={upload_result.uploaded_count} "
        f"chunks={upload_result.chunk_count} "
        f"store={upload_result.store_name or 'not-configured'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
