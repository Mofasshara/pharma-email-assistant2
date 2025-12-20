from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(results_file: str, min_ok_rate: float) -> None:
    path = Path(results_file)
    total = 0
    ok = 0

    with path.open(encoding="utf-8") as f:
        for line in f:
            total += 1
            rec = json.loads(line)
            out = rec.get("output") or {}
            rewritten = out.get("rewritten_email") if isinstance(out, dict) else str(out)

            if rewritten and len(rewritten.strip()) >= 30:
                ok += 1

    ok_rate = ok / total if total else 0.0
    print(f"OK rate: {ok_rate:.2%} ({ok}/{total})  min_required={min_ok_rate:.2%}")

    if ok_rate < min_ok_rate:
        raise SystemExit(1)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--results", required=True)
    p.add_argument("--min_ok_rate", type=float, default=0.8)
    args = p.parse_args()
    main(args.results, args.min_ok_rate)
