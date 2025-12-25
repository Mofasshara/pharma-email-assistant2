import json

from storage.banking_audit_log import AUDIT_FILE


def load_by_trace_id(trace_id: str):
    if not AUDIT_FILE.exists():
        return None

    with AUDIT_FILE.open(encoding="utf-8") as f:
        for line in f:
            event = json.loads(line)
            if event["trace_id"] == trace_id:
                return event
    return None


def search_reviews(risk_level: str):
    results = []
    if not AUDIT_FILE.exists():
        return results

    with AUDIT_FILE.open(encoding="utf-8") as f:
        for line in f:
            event = json.loads(line)
            if event.get("risk_level") == risk_level:
                results.append(event)
    return results
