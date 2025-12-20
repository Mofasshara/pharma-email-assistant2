import logging
import time
import uuid
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from requests import RequestException
from agents.orchestrator import handle_request
from agents.tools.rewrite_tool import REWRITE_API_URL
from agents.tools.exceptions import ToolServiceError

logger = logging.getLogger(__name__)

app = FastAPI(title="Agent Orchestrator API")


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


class AgentRequest(BaseModel):
    email: str
    audience: str


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "request_id": request_id},
    )


@app.post("/agent/handle")
def agent_handle(payload: AgentRequest, request: Request):
    request_id = getattr(request.state, "request_id", None)
    try:
        return {
            "response": handle_request(
                payload.email, payload.audience, request_id=request_id
            ),
            "request_id": request_id,
        }
    except ToolServiceError as exc:
        logger.warning(f"Tool failure: {exc}")
        raise HTTPException(status_code=502, detail=str(exc))
    except RequestException as exc:
        logger.warning(f"Downstream HTTP failure: {exc}")
        raise HTTPException(status_code=502, detail="Downstream service error")
    except HTTPException:
        # propagate existing HTTP exceptions (e.g., validation)
        raise
    except Exception:
        logger.exception("Agent handle failed")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/agent/health")
def agent_health():
    return {"status": "ok", "service": "agent-orchestrator"}


@app.get("/agent/deps")
def agent_deps(request: Request):
    request_id = getattr(request.state, "request_id", None)

    if not REWRITE_API_URL:
        raise HTTPException(status_code=502, detail="Rewrite URL not configured")

    url = f"{REWRITE_API_URL}/"
    start = time.perf_counter()
    try:
        resp = requests.get(url, timeout=(5, 5))
        resp.raise_for_status()
        latency_ms = int((time.perf_counter() - start) * 1000)
        return {
            "rewrite": "ok",
            "rewrite_url": url,
            "latency_ms": latency_ms,
            "request_id": request_id,
        }
    except RequestException as exc:
        latency_ms = int((time.perf_counter() - start) * 1000)
        status = getattr(getattr(exc, "response", None), "status_code", None)
        raise HTTPException(
            status_code=502,
            detail=f"Rewrite health check failed. url={url} status={status} latency_ms={latency_ms} request_id={request_id}",
        )
