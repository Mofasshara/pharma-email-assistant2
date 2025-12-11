import csv
import sys
from pathlib import Path

# Ensure project root is on sys.path so `src` resolves when running from anywhere.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.services.rewrite_service import rewrite_email_llm

with open("evaluation/eval_set.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print("\n=== ORIGINAL ===")
        print(row["original_email"])
        print("=== REWRITTEN ===")
        result = rewrite_email_llm(row["original_email"], row["audience"])
        print(result)
