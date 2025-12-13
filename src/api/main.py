from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from loguru import logger
import traceback

from src.logging_utils import log_request
from src.services.rewrite_service import rewrite_email_llm


class EmailRequest(BaseModel):
    text: str
    audience: str


app = FastAPI(port=8000)


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
        output = rewrite_email_llm(payload.text, payload.audience)
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
