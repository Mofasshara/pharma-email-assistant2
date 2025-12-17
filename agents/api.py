import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.orchestrator import handle_request

logger = logging.getLogger(__name__)

app = FastAPI(title="Agent Orchestrator API")


class AgentRequest(BaseModel):
    email: str
    audience: str


@app.post("/agent/handle")
def agent_handle(payload: AgentRequest):
    try:
        return {
            "response": handle_request(payload.email, payload.audience)
        }
    except Exception as exc:
        # Log the root cause so we can see the failure in the server console.
        logger.exception("Agent handle failed")
        raise HTTPException(status_code=500, detail="Internal server error")
