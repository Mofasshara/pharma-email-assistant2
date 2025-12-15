import sys
import json
from pathlib import Path

# Ensure project root is on sys.path before importing prompt_playground modules
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from prompt_playground.judge import judge

def main(results_file: str):
    in_path = Path(results_file)
    out_path = in_path.with_name(in_path.stem + "__scored.jsonl")

    with in_path.open(encoding="utf-8") as f, out_path.open("w", encoding="utf-8") as out_f:
        for line in f:
            record = json.loads(line)
            output = record["output"]
            rewritten = output.get("rewritten_email") if isinstance(output, dict) else str(output)

            scores = judge(
                input_email=record["input_email"],
                output_email=rewritten,
                audience=record["audience"],
            )
            record["scores"] = scores
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("Saved scored results:", out_path)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    args = p.parse_args()
    main(args.file)
