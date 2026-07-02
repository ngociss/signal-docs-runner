from __future__ import annotations

import os

from dotenv import load_dotenv
from google import genai


SYSTEM_PROMPT = """You are OptiBot, the customer-support bot for OptiSigns.com.
Tone: helpful, factual, concise.
Only answer using the uploaded docs.
Max 5 bullet points; else link to the doc.
Cite up to 3 "Article URL:" lines per reply."""


def main() -> int:
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    store_name = os.getenv("GEMINI_FILE_SEARCH_STORE_NAME")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is required.")
    if not store_name:
        raise RuntimeError("GEMINI_FILE_SEARCH_STORE_NAME is required.")

    question = "How do I add a YouTube video?"
    client = genai.Client(api_key=api_key)
    interaction = client.interactions.create(
        model="gemini-3.5-flash",
        input=f"{SYSTEM_PROMPT}\n\nQuestion: {question}",
        tools=[
            {
                "type": "file_search",
                "file_search_store_names": [store_name],
            }
        ],
    )

    for step in interaction.steps:
        if step.type != "model_output":
            continue
        for content in step.content:
            if content.type == "text":
                print(content.text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
