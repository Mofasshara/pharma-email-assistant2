import requests


def rewrite_email(text: str, audience: str) -> str:
    resp = requests.post(
        "https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/rewrite",
        json={"text": text, "audience": audience},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json().get("rewritten_email", "")
