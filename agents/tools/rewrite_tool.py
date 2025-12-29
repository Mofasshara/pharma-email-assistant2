import os
import requests


def normalize_base_url(url: str) -> str:
    if not url:
        return ""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")


REWRITE_BASE_URL = normalize_base_url(os.getenv("REWRITE_API_BASE"))
REWRITE_API_URL = REWRITE_BASE_URL


def rewrite_email(text: str, audience: str, request_id: str | None = None):
    if not REWRITE_BASE_URL:
        raise RuntimeError("REWRITE_API_BASE environment variable is not set")

    url = f"{REWRITE_BASE_URL}/rewrite"

    try:
        headers = {}
        if request_id:
            headers["X-Request-ID"] = request_id

        resp = requests.post(
            url,
            json={
                "text": text,
                "audience": audience,
            },
            headers=headers,
            timeout=(5, 30),  # 5s connect, 30s read
        )
        resp.raise_for_status()
        return resp.json()

    except requests.exceptions.Timeout:
        raise RuntimeError(
            f"Rewrite service timed out calling {url}"
        )

    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            f"Rewrite service connection error calling {url}: {str(e)}"
        )

    except requests.exceptions.HTTPError as e:
        raise RuntimeError(
            f"Rewrite service returned {resp.status_code}: {resp.text}"
        ) from e
