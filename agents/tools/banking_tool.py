import os
import requests


def normalize_base_url(url: str) -> str:
    if not url:
        return ""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")


BANKING_BASE_URL = normalize_base_url(os.getenv("BANKING_API_BASE"))


def banking_rewrite(email: str, audience: str, language: str = "en", request_id: str | None = None):
    if not BANKING_BASE_URL:
        raise RuntimeError("BANKING_API_BASE environment variable is not set")

    url = f"{BANKING_BASE_URL}/banking/rewrite"
    headers = {}
    if request_id:
        headers["X-Request-ID"] = request_id

    try:
        resp = requests.post(
            url,
            json={
                "email": email,
                "audience": audience,
                "language": language,
            },
            headers=headers,
            timeout=(5, 30),
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout as exc:
        raise RuntimeError(f"Banking rewrite timed out calling {url}") from exc
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            f"Banking rewrite connection error calling {url}: {str(exc)}"
        ) from exc
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(
            f"Banking rewrite returned {resp.status_code}: {resp.text}"
        ) from exc
