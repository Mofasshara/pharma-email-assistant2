from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from loguru import logger
import traceback


class EmailRequest(BaseModel):
    text: str
    audience: str


app = FastAPI(port=8000)


@app.get("/")
def health():
    return {"status": "ok"}


from src.services.rewrite_service import rewrite_email_llm


@app.post("/rewrite")
def rewrite_email(payload: EmailRequest):
    logger.info(f"Incoming request: {payload.dict()}")
    try:
        output = rewrite_email_llm(payload.text, payload.audience)
        logger.info("Rewrite successful")
        return output
    except Exception as exc:
        logger.error(f"Error: {exc}")
        return {"error": "internal_error"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Internal Server Error")
    traceback.print_exc()

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )
