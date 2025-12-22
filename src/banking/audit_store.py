import json
from collections import deque
from pathlib import Path
from typing import Any

AUDIT_DIR = Path("/home") / "audit"
AUDIT_FILE = AUDIT_DIR / "banking_rewrites.jsonl"
REVIEW_EVENTS_FILE = AUDIT_DIR / "banking_review_events.jsonl"


def append_record(record: dict[str, Any]) -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=True) + "\n")


def get_record(trace_id: str) -> dict[str, Any] | None:
    if not AUDIT_FILE.exists():
        return None
    latest = None
    with AUDIT_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("trace_id") == trace_id:
                latest = record
    return latest


def list_records(limit: int = 50) -> list[dict[str, Any]]:
    if not AUDIT_FILE.exists():
        return []
    recent: deque[dict[str, Any]] = deque(maxlen=limit)
    with AUDIT_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            recent.append(record)
    return list(recent)


def append_review_event(event: dict[str, Any]) -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    with REVIEW_EVENTS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=True) + "\n")
