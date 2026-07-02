from __future__ import annotations

from dataclasses import dataclass
import math
import os
import time

from google import genai

from vector_store.manifest import ArticleChanges


MAX_TOKENS_PER_CHUNK = 512
MAX_OVERLAP_TOKENS = 64


@dataclass(frozen=True)
class UploadResult:
    uploaded_count: int
    chunk_count: int
    file_ids_by_url: dict[str, str]
    store_name: str | None = None


def upload_changed_articles(changes: ArticleChanges) -> UploadResult:
    """Upload added and updated Markdown files to the configured vector store."""
    changed = changes.added + changes.updated
    if not changed:
        store_name = os.getenv("GEMINI_FILE_SEARCH_STORE_NAME") or None
        return UploadResult(
            uploaded_count=0,
            chunk_count=0,
            file_ids_by_url={},
            store_name=store_name,
        )

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is required to upload changed Markdown files to Gemini File Search."
        )

    client = genai.Client(api_key=api_key)
    store_name = os.getenv("GEMINI_FILE_SEARCH_STORE_NAME") or _create_file_search_store(client)

    file_ids_by_url: dict[str, str] = {}
    chunk_count = 0

    for article in changed:
        operation = client.file_search_stores.upload_to_file_search_store(
            file=str(article.path),
            file_search_store_name=store_name,
            config={
                "display_name": article.path.name,
                "chunking_config": {
                    "white_space_config": {
                        "max_tokens_per_chunk": MAX_TOKENS_PER_CHUNK,
                        "max_overlap_tokens": MAX_OVERLAP_TOKENS,
                    }
                },
            },
        )
        operation = _wait_for_operation(client, operation)
        file_ids_by_url[article.url] = _operation_resource_name(operation)
        chunk_count += _estimate_chunk_count(article.path.read_text(encoding="utf-8"))

    return UploadResult(
        uploaded_count=len(changed),
        chunk_count=chunk_count,
        file_ids_by_url=file_ids_by_url,
        store_name=store_name,
    )


def _create_file_search_store(client: genai.Client) -> str:
    store = client.file_search_stores.create(
        config={
            "display_name": "signal-docs-runner",
            "embedding_model": "models/gemini-embedding-2",
        }
    )
    print(f"Created Gemini File Search store: {store.name}")
    print("Add this to .env as GEMINI_FILE_SEARCH_STORE_NAME to reuse it on later runs.")
    return store.name


def _wait_for_operation(client: genai.Client, operation: object) -> object:
    while not getattr(operation, "done", False):
        time.sleep(5)
        operation = client.operations.get(operation)

    error = getattr(operation, "error", None)
    if error:
        raise RuntimeError(f"Gemini File Search upload failed: {error}")

    return operation


def _operation_resource_name(operation: object) -> str:
    response = getattr(operation, "response", None)
    name = getattr(response, "name", None)
    if name:
        return name

    return getattr(operation, "name", "")


def _estimate_chunk_count(text: str) -> int:
    words = len(text.split())
    if words == 0:
        return 0

    effective_chunk_size = MAX_TOKENS_PER_CHUNK - MAX_OVERLAP_TOKENS
    return max(1, math.ceil(words / effective_chunk_size))
