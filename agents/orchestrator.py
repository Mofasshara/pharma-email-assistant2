import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agents.tools.rag_tool import rag_search
from agents.tools.rewrite_tool import rewrite_email
from agents.tools.banking_tool import banking_rewrite
from agents.tools.eval_tool import evaluate_output

# Load environment variables (e.g., OPENAI_API_KEY) from .env
load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")


def route_request(user_input: str) -> str:
    decision = llm.invoke(
        f"Decide route for this request:\n{user_input}"
    )
    return str(decision).strip()


def handle_request(
    text: str,
    audience: str,
    domain: str | None = None,
    request_id: str | None = None,
):
    if os.getenv("FORCE_RAG", "").lower() in {"1", "true", "yes"}:
        result = rag_search(text, request_id=request_id)
        if not evaluate_output(result):
            return "Response blocked due to policy."
        return result

    if domain and domain.lower() == "banking":
        result = banking_rewrite(text, audience, request_id=request_id)
        if not evaluate_output(result):
            return "Response blocked due to policy."
        return result

    route = route_request(text)

    if "RAG" in route:
        result = rag_search(text, request_id=request_id)
    else:
        result = rewrite_email(text, audience, request_id=request_id)

    if not evaluate_output(result):
        return "Response blocked due to policy."

    return result
