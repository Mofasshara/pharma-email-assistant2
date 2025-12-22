import json
from datetime import datetime


def log_event(trace_id: str, event: dict) -> None:
    record = {
        "trace_id": trace_id,
        "timestamp": datetime.utcnow().isoformat(),
        **event,
    }
    print(json.dumps(record))
