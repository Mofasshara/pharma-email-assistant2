import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml
from rich import print

from src.services.rewrite_service import rewrite_email_llm

BASE = Path("prompt_playground")
PROMPTS_DIR = BASE / "prompts"
RESULTS_DIR = BASE / "results"
DATASETS_DIR = BASE / "datasets"


def load_registry() -> dict:
    return yaml.safe_load((PROMPTS_DIR / "registry.yaml").read_text(encoding="utf-8"))


def load_prompt_text(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")


def main(prompt_key: str, dataset_file: str) -> None:
    prompts = load_registry().get("prompts", {})
    prompt_meta = prompts.get(prompt_key)

    if not prompt_meta:
        available = ", ".join(sorted(prompts.keys())) if prompts else "<none>"
        raise SystemExit(f"Unknown prompt_key='{prompt_key}'. Available: {available}")

    dataset_path = DATASETS_DIR / dataset_file
    if not dataset_path.exists():
        raise SystemExit(f"Dataset not found: {dataset_path}")

    # If registry.yaml has: prompts: { key: { file: "rewrite_medical_v2.txt" } }
    # then we load it. If not, we keep it as empty string for now.
    prompt_text = ""
    if isinstance(prompt_meta, dict) and "file" in prompt_meta:
        prompt_text = load_prompt_text(prompt_meta["file"])

    df = pd.read_csv(dataset_path)

    run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = RESULTS_DIR / f"{prompt_key}__{run_id}.jsonl"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[bold]Running[/bold] {prompt_key} on {dataset_file}")
    with out_path.open("w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            input_email = row["input_email"]
            audience = row["audience"]

            # Uses your existing LLM rewrite function
            # If your rewrite_email_llm doesn't accept prompt_text yet, that's OK:
            # we store it in the record for traceability.
            output = rewrite_email_llm(input_email, audience)

            record = {
                "id": int(row["id"]),
                "audience": audience,
                "input_email": input_email,
                "prompt_key": prompt_key,
                "prompt_text": prompt_text,
                "output": output,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"[green]Saved results to[/green] {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--dataset", required=True)
    args = parser.parse_args()
    main(args.prompt, args.dataset)
