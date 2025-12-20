import os
import requests
from requests.exceptions import RequestException, Timeout
from agents.tools.exceptions import ToolServiceError

RAG_API_URL = (os.getenv("RAG_API_URL") or "https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net").rstrip("/")


def rag_search(query: str, request_id: str | None = None) -> str:
    if not RAG_API_URL:
        raise ToolServiceError("RAG tool: RAG_API_URL is not set.")

    url = f"{RAG_API_URL}/rag/ask"

    try:
        resp = requests.post(
            url,
            json={"query": query},
            timeout=(5, 30),  # connect, read
        )
        resp.raise_for_status()
    except Timeout as e:
        raise ToolServiceError(
            f"RAG tool timeout. url={url} request_id={request_id or 'n/a'}"
        ) from e
    except RequestException as e:
        status = getattr(getattr(e, "response", None), "status_code", None)
        body = ""
        if getattr(e, "response", None) is not None:
            try:
                body = e.response.text[:500]
            except Exception:
                body = "<unable to read response body>"
        req_id = request_id or "n/a"
        msg = f"RAG tool failure. url={url} status={status} request_id={req_id} body={body}"
        raise ToolServiceError(msg) from e

    data = resp.json()
    # Expect "answer" but fall back to entire payload for debugging.
    return data.get("answer") or data.get("result") or str(data)
