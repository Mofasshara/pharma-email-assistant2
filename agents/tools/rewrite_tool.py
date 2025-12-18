import os
import requests

REWRITE_API_URL = os.getenv("REWRITE_API_URL", "").rstrip("/")

def rewrite_email(text: str, audience: str) -> str:
    if not REWRITE_API_URL:
        raise RuntimeError("REWRITE_API_URL is not set")

    resp = requests.post(
        f"{REWRITE_API_URL}/rewrite",
        json={"text": text, "audience": audience},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    # adjust key based on your rewrite API response
    return data.get("rewritten_email") or data.get("response") or str(data)
