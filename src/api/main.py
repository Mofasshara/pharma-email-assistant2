import uuid
from typing import Any
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from loguru import logger
import traceback

from src.logging_utils import log_request
from src.safety_checks import basic_safety_check
from src.services.rewrite_service import rewrite_email_llm
from src.services.rag_client import fetch_rag_answer, should_use_rag


class EmailRequest(BaseModel):
    text: str
    audience: str


app = FastAPI(
    title="Pharma Email Rewriter API",
    port=8000,
    description=(
        "<details><summary>Quick User Guide (click to expand)</summary>\n\n"
        "**Purpose:** Rewrite pharma emails with compliance-aware prompts.\n\n"
        "**How to use:**\n"
        "1) Open `/docs` and expand `POST /rewrite`.\n"
        "2) Paste the request body and click **Execute**.\n"
        "</details>"
    ),
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    logger.info(f"[{request_id}] Incoming {request.method} {request.url.path}")
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(f"[{request_id}] Unhandled error")
        raise
    response.headers["X-Request-ID"] = request_id
    logger.info(f"[{request_id}] Completed {response.status_code}")
    return response


class FeedbackRequest(BaseModel):
    input_text: str
    audience: str
    output: dict
    rating: int  # 1-5
    comments: str | None = None


@app.get(
    "/",
    description="Health check for the pharma rewrite service.",
)
def health():
    return {"status": "ok"}


@app.post(
    "/rewrite",
    description=(
        "Rewrite a pharma email using the audience-specific prompt.\n\n"
        "**Example:**\n"
        "```json\n"
        "{\n"
        "  \"text\": \"This product guarantees the best patient outcomes.\",\n"
        "  \"audience\": \"medical affairs\"\n"
        "}\n"
        "```"
    ),
)
def rewrite_email(payload: EmailRequest):
    logger.info(f"Incoming request: {payload.dict()}")
    try:
        if not basic_safety_check(payload.text):
            logger.warning("Safety check failed for input text")
            return {
                "error": "Safety check failed",
                "reason": "Potential hallucination or unsafe claim"
            }

        rag_info = None
        text_for_rewrite = payload.text
        if should_use_rag(payload.text):
            rag_info = fetch_rag_answer(payload.text)
            if rag_info:
                text_for_rewrite = (
                    f"{payload.text}\n\n"
                    "Reference context (internal documents):\n"
                    f"{rag_info['answer']}"
                )

        output: dict[str, Any] = rewrite_email_llm(
            text_for_rewrite,
            payload.audience,
        )
        if not basic_safety_check(output["rewritten_email"]):
            logger.warning("Safety check failed for rewritten email")
            return {
                "error": "Safety check failed",
                "reason": "Potential hallucination or unsafe claim"
            }
        if rag_info:
            output["rag_used"] = True
            output["rag_sources"] = rag_info.get("sources", [])
        logger.info("Rewrite successful")
        log_request(payload.text, payload.audience, output, feedback=None)
        return output
    except Exception as exc:
        logger.error(f"Error: {exc}")
        return {"error": "internal_error"}


@app.post(
    "/feedback",
    description=(
        "Submit feedback on a rewrite to improve quality.\n\n"
        "**Example:**\n"
        "```json\n"
        "{\n"
        "  \"input_text\": \"This product guarantees the best patient outcomes.\",\n"
        "  \"audience\": \"medical affairs\",\n"
        "  \"output\": {\"rewritten_email\": \"Example output...\"},\n"
        "  \"rating\": 5,\n"
        "  \"comments\": \"Clear and compliant.\"\n"
        "}\n"
        "```"
    ),
)
def submit_feedback(payload: FeedbackRequest):
    feedback_data = {
        "rating": payload.rating,
        "comments": payload.comments,
    }
    log_request(
        input_text=payload.input_text,
        audience=payload.audience,
        output=payload.output,
        feedback=feedback_data,
    )
    return {"status": "feedback_recorded"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Internal Server Error")
    traceback.print_exc()

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )
