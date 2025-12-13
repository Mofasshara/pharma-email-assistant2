# pharma-email-assistant2
AI-powered email rewriting assistant for medical/pharma use cases.
![Architecture Diagram](Untitled-2025-12-11-1423.png)

## Roadmap (Upcoming Weeks)
- Audience-specific rewriting prompts
- Compliance checker agent
- Add hallucination evaluation
- Add Docker deployment to Azure
## System Architecture
![architecture](docs/architecture.png)
## How logging works
- Every request to the `/rewrite` endpoint is recorded using Loguru.
- Logs include: input text, audience type, output email, and timestamp.
- Sensitive data (names, IDs, emails) should be anonymized before saving.
- Logs are stored in `logs/requests.jsonl` for later review.

## How to submit feedback
- After testing a rewritten email, you can rate or comment on its quality.
- Feedback is captured via the `/feedback` endpoint (to be added in Week 3).
- Each feedback entry links to the original request and output.
- This helps identify strong examples for fine-tuning and weak ones to improve.

## How to export dataset for evaluation
- Logged requests and feedback can be exported into a dataset file.
- Example: run a script that reads `logs/requests.jsonl` and outputs `dataset.csv`.
- The dataset includes: input, audience, output, feedback, and compliance tags.
- This dataset is then used for evaluation or fine-tuning in Month 3.
