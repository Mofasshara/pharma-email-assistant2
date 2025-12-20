import json
from pathlib import Path

IN_FILE = Path("logs/requests.jsonl")
OUT_FILE = Path("finetune/dataset.jsonl")
OUT_FILE.parent.mkdir(exist_ok=True)

with IN_FILE.open() as f, OUT_FILE.open("w") as out:
    for line in f:
        r = json.loads(line)
        feedback = r.get("feedback") or {}
        if feedback.get("rating", 0) >= 4:
            audience = r["audience"]
            input_text = r["input_text"]
            prompt = f"Rewrite the following email for {audience}:\n{input_text}"
            completion = (r.get("output") or {}).get("rewritten_email")
            out.write(json.dumps({
                "prompt": prompt,
                "completion": completion
            }) + "\n")

print("Fine-tuning dataset created")
