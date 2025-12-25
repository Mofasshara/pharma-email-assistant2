import json
from pathlib import Path

AUDIT_FILE = Path("storage/banking_audit_log.jsonl")


def save_event(event: dict) -> None:
    AUDIT_FILE.parent.mkdir(exist_ok=True)
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=True) + "\n")
