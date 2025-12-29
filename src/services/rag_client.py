import os
from typing import Any, Dict, Optional

import requests


_RAG_API_URL = (os.getenv("RAG_API_URL") or "").strip().rstrip("/")


def should_use_rag(text: str) -> bool:
    lowered = text.lower()
    keywords = [
        "guideline",
        "regulatory",
        "protocol",
        "sop",
        "adverse event",
        "labeling",
        "compliance",
    ]
    return any(word in lowered for word in keywords)


def fetch_rag_answer(
    query: str,
    request_id: str | None = None,
) -> Optional[Dict[str, Any]]:
    if not _RAG_API_URL:
        return None

    url = f"{_RAG_API_URL}/rag/ask"
    headers = {}
    if request_id:
        headers["X-Request-ID"] = request_id

    try:
        resp = requests.post(
            url,
            json={"query": query},
            headers=headers,
            timeout=(5, 30),
        )
        resp.raise_for_status()
    except requests.RequestException:
        return None

    data = resp.json()
    answer = data.get("answer")
    if not answer:
        return None
    return {
        "answer": answer,
        "sources": data.get("sources", []),
    }
