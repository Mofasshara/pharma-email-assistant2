from fastapi import FastAPI
from pydantic import BaseModel
from rag.retrieval.rag_pipeline import get_rag_chain

app = FastAPI(title="RAG Service API")
qa = get_rag_chain()

class Question(BaseModel):
    query: str

@app.get("/rag/health")
def rag_health():
    return {"status": "ok", "service": "rag"}

@app.post("/rag/ask")
def ask_rag(payload: Question):
    # RunnableSequence is not directly callable; use invoke to run the chain.
    result = qa.invoke(payload.query)

    if not result["source_documents"]:
        return {
            "answer": "I cannot find relevant information in the provided documents.",
            "sources": []
        }

    return {
        "answer": result["result"],
        "sources": [
            doc.metadata.get("source") for doc in result["source_documents"]
        ]
    }
