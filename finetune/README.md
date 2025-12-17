# Fine-tuning Assets
# Week 8 — LoRA Fine-tuning (PEFT) for Pharma Email Rewriting

## What this is
A reproducible LoRA fine-tuning pipeline to improve style/structure consistency for pharma email rewriting prompts.

## Base model
- TinyLlama/TinyLlama-1.1B-Chat-v1.0 (used to validate pipeline on Colab GPU)

## Dataset
- JSONL in instruction format with a single `text` field
- Generated from rewrite examples (and can scale later from production logs)

## Training
- PEFT: LoRA (r=8, alpha=16, target modules: q_proj, v_proj)
- Trainer: TRL SFTTrainer
- Precision: bf16
- Output checkpoints: `lora-output/checkpoint-*`
- Final adapter artifact: `lora-adapter-final` (exported from latest checkpoint)

## Evaluation
- Compared base vs fine-tuned outputs on:
  - Regulatory AE request
  - Medical Affairs summary
  - Patient-friendly rewrite
- See: `finetune/notes/eval_report.txt`

## Key insight (RAG vs Fine-tuning)
- Fine-tuning improves tone/format consistency
- RAG (Week 7) is preferred for factual grounding + citations

This directory contains datasets and scripts for building and converting fine-tune data.

## Structure
- data/
  - dataset.jsonl (source samples)
  - dataset_sft.jsonl (SFT-ready; optional if sensitive)
- scripts/
  - build_finetune_dataset.py (filters logs into dataset.jsonl)
  - convert_dataset_for_sft.py (rewrites to SFT format)
- notes/
  - eval_report.txt (evaluation notes)

## Usage
1) Build dataset from logs: `python scripts/build_finetune_dataset.py`
   - Reads `logs/requests.jsonl`, keeps entries with feedback rating >= 4, writes `finetune/data/dataset.jsonl`.
2) Convert for SFT: `python finetune/scripts/convert_dataset_for_sft.py`
   - Produces `finetune/data/dataset_sft.jsonl` with instruction/response text payload.

## Notes
- Keep sensitive data out of version control; treat `dataset_sft.jsonl` as optional if it contains sensitive content.
- Ensure `.env` has required keys before running scripts.
