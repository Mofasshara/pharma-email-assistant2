# ruff: noqa: E402
import sys
import yaml
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
from rich import print

# Ensure project root is on sys.path so "src" imports work when running from CLI
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.services.rewrite_service import rewrite_email_llm

BASE = Path("prompt_playground")
PROMPTS_DIR = BASE / "prompts"
RESULTS_DIR = BASE / "results"
DATASETS_DIR = BASE / "datasets"

def load_registry():
    return yaml.safe_load((PROMPTS_DIR / "registry.yaml").read_text())

def load_prompt_text(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text()

def main(prompt_key: str, dataset_file: str):
    reg = load_registry()["prompts"]
    dataset_path = DATASETS_DIR / dataset_file

    df = pd.read_csv(dataset_path)

    run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = RESULTS_DIR / f"{prompt_key}__{run_id}.jsonl"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[bold]Running[/bold] {prompt_key} on {dataset_file}")
    for _, row in df.iterrows():
        input_email = row["input_email"]
        audience = row["audience"]

        # Uses your existing LLM rewrite function
        output = rewrite_email_llm(input_email, audience)

        record = {
            "id": int(row["id"]),
            "audience": audience,
            "input_email": input_email,
            "prompt_key": prompt_key,
            "output": output,
        }
        out_path.write_text("", encoding="utf-8") if not out_path.exists() else None
        with out_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"[green]Saved results to[/green] {out_path}")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", required=True)
    p.add_argument("--dataset", required=True)
    args = p.parse_args()
    main(args.prompt, args.dataset)
