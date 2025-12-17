from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agents.tools.rag_tool import rag_search
from agents.tools.rewrite_tool import rewrite_email
from agents.tools.eval_tool import evaluate_output

# Load environment variables (e.g., OPENAI_API_KEY) from .env
load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")


def route_request(user_input: str) -> str:
    decision = llm.invoke(
        f"Decide route for this request:\n{user_input}"
    )
    return str(decision).strip()


def handle_request(text: str, audience: str):
    route = route_request(text)

    if "RAG" in route:
        result = rag_search(text)
    else:
        result = rewrite_email(text, audience)

    if not evaluate_output(result):
        return "Response blocked due to policy."

    return result
