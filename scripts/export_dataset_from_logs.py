import json
import csv
from pathlib import Path

LOG_FILE = Path("logs/requests.jsonl")
OUT_FILE = Path("evaluation/dataset_from_logs.csv")


def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open(encoding="utf-8") as f:
        with OUT_FILE.open("w", newline="", encoding="utf-8") as out_f:
            writer = csv.writer(out_f)
            writer.writerow(
                ["input_text", "audience", "rewritten_email", "rating", "comments"]
            )
            for line in f:
                record = json.loads(line)
                output = record.get("output") or {}
                feedback = record.get("feedback") or {}
                writer.writerow([
                    record.get("input_text", ""),
                    record.get("audience", ""),
                    output.get("rewritten_email", ""),
                    feedback.get("rating", ""),
                    feedback.get("comments", ""),
                ])


if __name__ == "__main__":
    main()
