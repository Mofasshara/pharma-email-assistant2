#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

import requests

BASE_URL = "http://localhost:8081"
INPUT_PATH = Path("evidence/banking/sample_requests.jsonl")
OUTPUT_PATH = Path("evidence/banking/batch_outputs.jsonl")


def main() -> None:
    if not INPUT_PATH.exists():
        raise SystemExit(f"Missing input file: {INPUT_PATH}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("", encoding="utf-8")

    counts = Counter()

    with INPUT_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            resp = requests.post(
                f"{BASE_URL}/banking/rewrite",
                json=payload,
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            counts[data.get("risk_level", "unknown")] += 1

            record = {
                "request": payload,
                "response": data,
            }
            with OUTPUT_PATH.open("a", encoding="utf-8") as out:
                out.write(json.dumps(record, ensure_ascii=True) + "\n")

    print("Risk level counts:")
    for key in sorted(counts):
        print(f"- {key}: {counts[key]}")


if __name__ == "__main__":
    main()
