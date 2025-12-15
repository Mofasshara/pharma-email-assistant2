# Prompt Playground

## ?? What it is
A sandbox for testing and evaluating different prompt versions for the Pharma Email Assistant.  
This helps compare clarity, tone, and compliance across iterations.

---

## ?? How to run experiments
1. Add new prompt templates in `/src/prompts`.
2. Run the evaluation script (`evaluation/evaluate.py`) with your dataset.
3. Collect model outputs and score them manually or with an automated rubric.

---

## ?? How scoring works
- **Clarity**: Is the rewritten email easy to understand?
- **Tone**: Does it match the intended audience (medical, regulatory, patient)?
- **Compliance**: Does it respect pharma/regulatory constraints?

Scores are averaged across multiple test cases (scale: 1–5).

---

## ?? Example results table

| Prompt              | Clarity | Tone | Compliance |
|---------------------|---------|------|------------|
| rewrite_medical_v1  | 3.8     | 3.6  | 4.0        |
| rewrite_medical_v2  | 4.3     | 4.1  | 4.4        |

---

## ?? Why this matters in production
Evaluating prompts systematically ensures:
- Consistency across outputs
- Reduced risk of non-compliant messaging
- Better user trust and adoption
- Clear evidence of improvement when iterating prompts