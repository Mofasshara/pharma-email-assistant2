import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("logs/requests.jsonl")


def log_request(
    input_text: str,
    audience: str,
    output: dict,
    feedback: dict | None = None,
):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "input_text": input_text,
        "audience": audience,
        "output": output,
        "feedback": feedback,
        "latency_ms": output.get("metadata", {}).get("latency_ms"),
        "tokens": output.get("metadata", {}).get("tokens"),
        "model": output.get("metadata", {}).get("model"),
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
