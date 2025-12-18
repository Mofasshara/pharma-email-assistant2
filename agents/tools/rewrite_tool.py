import os
import requests
from requests.exceptions import RequestException, Timeout
from agents.tools.exceptions import ToolServiceError


def _normalize_base_url(raw: str) -> str:
    """
    Accepts:
      - https://example.com
      - http://example.com
      - example.com
    Returns:
      - https://example.com   (default scheme added)
    """
    raw = (raw or "").strip().rstrip("/")
    if not raw:
        return ""
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    return raw


REWRITE_API_URL = _normalize_base_url(os.getenv("REWRITE_API_URL"))


def rewrite_email(text: str, audience: str, request_id: str | None = None) -> str:
    if not REWRITE_API_URL:
        raise ToolServiceError(
            "Rewrite tool: REWRITE_API_URL is not set. "
            "Set it in Azure App Service → Environment variables."
        )

    url = f"{REWRITE_API_URL}/rewrite"
    payload = {"text": text, "audience": audience}

    try:
        resp = requests.post(url, json=payload, timeout=(5, 30))  # connect, read
        resp.raise_for_status()
    except Timeout as e:
        raise ToolServiceError(
            f"Rewrite tool timeout. url={url} request_id={request_id or 'n/a'}"
        ) from e
    except RequestException as e:
        status = getattr(getattr(e, "response", None), "status_code", None)
        body = ""
        if getattr(e, "response", None) is not None:
            try:
                body = e.response.text[:500]  # avoid huge logs
            except Exception:
                body = "<unable to read response body>"

        raise ToolServiceError(
            f"Rewrite tool failure. url={url} status={status} request_id={request_id or 'n/a'} body={body}"
        ) from e

    data = resp.json()
    return data.get("rewritten_email") or data.get("response") or str(data)
