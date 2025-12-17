import requests


def rag_search(query: str) -> str:
    resp = requests.post(
        "https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/rag/ask",
        json={"query": query},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json().get("answer", "")
