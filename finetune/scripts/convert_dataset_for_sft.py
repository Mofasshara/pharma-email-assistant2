import json
from pathlib import Path

IN_FILE = Path("finetune/data/dataset.jsonl")
OUT_FILE = Path("finetune/data/dataset_sft.jsonl")

with IN_FILE.open(encoding="utf-8") as f, OUT_FILE.open("w", encoding="utf-8") as out:
    for line in f:
        row = json.loads(line)

        prompt = row["prompt"]
        completion = row["completion"]

        # Replace placeholder completions if needed
        if completion.strip().lower() == "example":
            completion = (
                "Please provide the adverse event information as soon as possible."
            )

        text = f"""### Instruction:
Rewrite the following email for Regulatory.

### Input:
{prompt.splitlines()[-1]}

### Response:
{{\"rewritten_email\": \"{completion}\"}}"""

        out.write(json.dumps({"text": text}, ensure_ascii=False) + "\n")

print("Converted dataset saved to dataset_sft.jsonl")
