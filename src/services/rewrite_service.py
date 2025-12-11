import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print(os.getenv("OPENAI_API_KEY"))

def load_template(audience: str) -> str:
    mapping = {
        "medical affairs": "rewrite_medical.txt",
        "regulatory": "rewrite_regulatory.txt",
        "hcp": "rewrite_hcp.txt",
        "patient": "rewrite_patient.txt",
    }
    filename = mapping.get(audience.lower(), "rewrite_medical.txt")
    return open(f"src/prompts/{filename}").read()

def rewrite_email_llm(text: str, audience: str) -> str:
    template = load_template(audience)
    prompt = template.replace("{{text}}", text).replace("{{audience}}", audience)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    raw = completion.choices[0].message.content
    try:
        return json.loads(raw)
    except Exception:
        return {"error": "Model did not return JSON", "raw": raw}
