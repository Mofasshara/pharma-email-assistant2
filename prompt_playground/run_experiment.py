import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml
from rich import print

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.services.rewrite_service import rewrite_email_llm  # noqa: E402
from src.banking.rewrite_service import rewrite_banking_email  # noqa: E402
from src.banking.schemas import BankingRewriteRequest  # noqa: E402

BASE = Path("prompt_playground")
PROMPTS_DIR = BASE / "prompts"
RESULTS_DIR = BASE / "results"
DATASETS_DIR = BASE / "datasets"


def load_registry() -> dict:
    return yaml.safe_load((PROMPTS_DIR / "registry.yaml").read_text(encoding="utf-8"))


def load_prompt_text(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")


def main(prompt_key: str, dataset_file: str) -> None:
    prompts = load_registry()["prompts"]
    prompt_meta = prompts[prompt_key]
    prompt_file = prompt_meta["file"]
    prompt_domain = prompt_meta.get("domain")

    dataset_path = DATASETS_DIR / dataset_file
    df = pd.read_csv(dataset_path)

    run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = RESULTS_DIR / f"{prompt_key}__{run_id}.jsonl"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    prompt_text = load_prompt_text(prompt_file)

    print(f"[bold]Running[/bold] {prompt_key} on {dataset_file}")
    for _, row in df.iterrows():
        if "email" in row and pd.notna(row["email"]):
            input_email = row["email"]
        else:
            input_email = row["input_email"]
        audience = row["audience"]
        language = row["language"] if "language" in row and pd.notna(row["language"]) else "en"

        if prompt_domain == "banking":
            req = BankingRewriteRequest(
                email=input_email,
                audience=audience,
                language=language,
            )
            output = rewrite_banking_email(req).model_dump()
        else:
            # Uses your existing LLM rewrite function
            output = rewrite_email_llm(input_email, audience, prompt_override=prompt_text)

        record = {
            "id": int(row["id"]),
            "audience": audience,
            "input_email": input_email,
            "language": language,
            "prompt_key": prompt_key,
            "output": output,
        }

        with out_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"[green]Saved results to[/green] {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--dataset", required=True)
    args = parser.parse_args()
    main(args.prompt, args.dataset)
