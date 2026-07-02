# Signal Docs Runner

Daily documentation ingestion job for a customer-support assistant knowledge base.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.sample .env
```

Fill `.env` with your API keys and IDs.

## Run Locally

```bash
python main.py
```

The job scrapes support articles, converts them to Markdown, detects added or updated files, uploads only deltas to the vector store, and prints run counts.

## Docker

```bash
docker build -t signal-docs-runner .
docker run --env-file .env signal-docs-runner
```

## Assistant Prompt

```text
You are OptiBot, the customer-support bot for OptiSigns.com.
• Tone: helpful, factual, concise.
• Only answer using the uploaded docs.
• Max 5 bullet points; else link to the doc.
• Cite up to 3 "Article URL:" lines per reply.
```

## Daily Job

Logs: TODO

## Sample Answer Screenshot

TODO: Add screenshot showing the assistant answering "How do I add a YouTube video?" with cited article URLs.

## Chunking Strategy

TODO: Document final vector-store chunking behavior after upload implementation.

