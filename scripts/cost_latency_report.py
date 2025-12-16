import json
import pandas as pd
from pathlib import Path

LOG_FILE = Path("logs/requests.jsonl")
REPORT_FILE = Path("reports/cost_latency.csv")

rows = []
with LOG_FILE.open() as f:
    for line in f:
        r = json.loads(line)
        if r.get("tokens"):
            rows.append({
                "latency_ms": r["latency_ms"],
                "total_tokens": r["tokens"]["total_tokens"],
                "model": r["model"],
                "audience": r["audience"]
            })

df = pd.DataFrame(rows)

REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(REPORT_FILE, index=False)

print("Average latency (ms):", int(df["latency_ms"].mean()))
print("Average tokens per request:", int(df["total_tokens"].mean()))
print("\nTokens by audience:")
print(df.groupby("audience")["total_tokens"].mean())
print(f"\nCSV written to {REPORT_FILE}")
