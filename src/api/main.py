import uuid
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from loguru import logger
import traceback

from domains.banking.risk_rewriter.router import router as banking_router
from src.logging_utils import log_request
from src.safety_checks import basic_safety_check
from src.services.rewrite_service import rewrite_email_llm


class EmailRequest(BaseModel):
    text: str
    audience: str


app = FastAPI(port=8000)
app.include_router(banking_router)


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


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/rewrite")
def rewrite_email(payload: EmailRequest):
    logger.info(f"Incoming request: {payload.dict()}")
    try:
        if not basic_safety_check(payload.text):
            logger.warning("Safety check failed for input text")
            return {
                "error": "Safety check failed",
                "reason": "Potential hallucination or unsafe claim"
            }

        output = rewrite_email_llm(payload.text, payload.audience)
        if not basic_safety_check(output["rewritten_email"]):
            logger.warning("Safety check failed for rewritten email")
            return {
                "error": "Safety check failed",
                "reason": "Potential hallucination or unsafe claim"
            }
        logger.info("Rewrite successful")
        log_request(payload.text, payload.audience, output, feedback=None)
        return output
    except Exception as exc:
        logger.error(f"Error: {exc}")
        return {"error": "internal_error"}


@app.post("/feedback")
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
