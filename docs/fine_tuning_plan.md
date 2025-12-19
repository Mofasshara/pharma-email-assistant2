# Fine-tuning plan

## Overview
- **Goal:** Improve rewrite quality for medical/pharma emails by learning from real usage.
- **Approach:** Log anonymized examples, curate high-quality pairs, and fine-tune an open model to match domain tone, compliance, and clarity.

## Data logging
- **What is logged (anonymized):**
  - **Inputs:** Original email text, requested audience (e.g., Medical Affairs), selected style/tone.
  - **Outputs:** Model-rewritten email, final user-approved edits (if any).
  - **Metadata:** Timestamp, prompt version, model version, rewrite success flag, compliance flags.
- **What is NOT logged:** Personal identifiers, patient data, proprietary trial IDs, names, emails, phone numbers.
- **Anonymization safeguards:**
  - **PII scrubbing:** Regex rules for emails, phone numbers, names, IDs.
  - **Redaction:** Replace sensitive tokens with placeholders (e.g., `[PRODUCT]`, `[TRIAL_ID]`).
  - **Access control:** Logs stored with restricted permissions and rotation.

## Filtering good examples
- **Selection criteria:**
  - **Quality:** Clear, concise, professional tone; preserved intent; improved structure.
  - **Compliance:** No promotional claims; aligns with medical/pharma guidance; correct disclaimers.
  - **Signal strength:** Minimal post-edit deltas (model output ≈ user-approved final).
  - **Diversity:** Variety of audiences, intents (request, follow-up, clarification), and lengths.
- **Automatic filters:**
  - **Heuristics:** Length thresholds, forbidden phrases, grammar checks.
  - **Scoring:** Rule-based compliance score + readability score.
- **Human review:**
  - **Spot checks:** Reviewer confirms tone, accuracy, compliance.
  - **Labeling:** Tag each pair with audience, intent, and outcome (good/needs work).

## Fine-tuning an open model (Month 3)
- **Model choice:** Start with an open LLM suitable for instruction-tuning (e.g., a lightweight, permissively licensed model).
- **Data format:** JSONL with input-output pairs.
  - Example:
    ```json
    {"instruction": "Rewrite for Medical Affairs, formal tone", "input": "Hey, can you send the results asap?", "output": "Dear colleague, could you please share the study results at your earliest convenience? Thank you."}
    ```
- **Procedure:**
  - **1. Prepare dataset:** Export curated examples, ensure anonymization and balance.
  - **2. Split:** Train/validation/test (80/10/10).
  - **3. Training:** LoRA or adapter-based fine-tuning to keep compute low.
  - **4. Evaluation:** Measure BLEU/ROUGE for structure, human preference for tone/compliance, and task success rate.
  - **5. Safety pass:** Re-run compliance filters; add rejection rules for risky content.
- **Outputs:** A domain-tuned model checkpoint and a deployment plan with versioning and rollback.

## Improving domain performance
- **Metrics to track:**
  - **Rewrite acceptance rate:** Percent of model outputs used without major edits.
  - **Compliance score:** Automated + reviewer-confirmed pass rates.
  - **Clarity/readability:** Flesch/Kincaid + human ratings.
  - **Turnaround time:** Average time to produce a usable email.
- **Iterative improvements:**
  - **Prompt updates:** Refine system prompts with learned patterns (tone, disclaimers).
  - **Data refresh:** Periodically add new curated examples; remove low-signal pairs.
  - **Specialization:** Separate heads/prompts per audience (Medical Affairs, Regulatory, Clinical Ops).
  - **Guardrails:** Pre-checkers for forbidden claims and sensitive requests before generation.
- **Deployment considerations:**
  - **Versioning:** Tag model/prompt versions; log which version produced each rewrite.
  - **Rollback:** Keep previous stable model; quick revert if metrics dip.
  - **Monitoring:** Continuous logging with alerts for compliance or quality regressions.
