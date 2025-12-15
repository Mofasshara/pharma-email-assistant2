import json
from pathlib import Path
import statistics as stats


def avg_scores(file_path: str):
    scores = {"clarity": [], "tone": [], "compliance": []}
    with Path(file_path).open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            s = r.get("scores", {})
            for k in scores:
                if k in s:
                    scores[k].append(s[k])
    return {k: round(stats.mean(v), 2) if v else None for k, v in scores.items()}


def main(a: str, b: str):
    print("A:", a, avg_scores(a))
    print("B:", b, avg_scores(b))


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--a", required=True)
    p.add_argument("--b", required=True)
    args = p.parse_args()
    main(args.a, args.b)