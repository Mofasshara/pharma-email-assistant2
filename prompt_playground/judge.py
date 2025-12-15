import os
import json
from openai import OpenAI
from src.settings import settings

client = OpenAI(api_key=settings.openai_api_key)

JUDGE_PROMPT = """
You are an expert evaluator for pharma communication.

Score the rewritten email from 1 to 5 on:
1) clarity
2) tone_appropriateness
3) compliance_safety

Return ONLY valid JSON:
{
  "clarity": <1-5>,
  "tone": <1-5>,
  "compliance": <1-5>,
  "notes": "<short justification>"
}
"""

def judge(input_email: str, output_email: str, audience: str) -> dict:
    msg = f"""
Audience: {audience}

Original:
{input_email}

Rewritten:
{output_email}
"""
    res = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": JUDGE_PROMPT},
            {"role": "user", "content": msg},
        ],
        temperature=0,
    )
    raw = res.choices[0].message.content
    return json.loads(raw)