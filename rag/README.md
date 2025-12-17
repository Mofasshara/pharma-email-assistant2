# RAG README
# RAG Pipeline Overview

## 🧠 What is RAG?
RAG (Retrieval-Augmented Generation) combines a vector-based document search with an LLM to answer questions using external knowledge. It retrieves relevant chunks from a document store and feeds them into the model for context-aware responses.

## 🧱 Architecture (optional)
- Ingestion: Load and chunk PDFs → embed into vector DB
- Retrieval: Query → retrieve relevant chunks → rerank → generate answer

## 🔄 Ingestion vs Retrieval
- **Ingestion**: One-time process to prepare documents (PDFs → chunks → embeddings)
- **Retrieval**: Real-time process to answer user queries using those chunks

## 🧪 Example API Calls


### POST /rag/ask
```json
{
  "query": "What are EMA requirements for stability testing?"
}
{
  "answer": "...",
  "sources": ["stability_guideline.pdf"]
}

---

### ✅ 3. Save the file
- Press **Ctrl+S** (Windows) or **Cmd+S** (Mac)

---

## 🧭 Step 2 — Commit Week 7

### ✅ 1. Open Source Control tab
- Click the **branch icon** in the left sidebar (Source Control)

### ✅ 2. Stage your changes
- You’ll see `rag/README.md` under **Changes**
- Click the **+** icon next to it (or click `...` → Stage All Changes)

### ✅ 3. Write your commit message
- In the message box, type:


This directory holds the Retrieval-Augmented Generation (RAG) pieces used by the app.

## Setup
1) Create and activate the virtual environment (or reuse `venv`).
2) Install deps: `pip install -r requirements.txt`.
3) Add your OpenAI key to `.env` (already loaded via `dotenv`):
   - `OPENAI_API_KEY=...`

## Running the RAG API
- Start the server from repo root (venv active):
  - `uvicorn rag.api.main:app --reload`
- Open docs at `http://127.0.0.1:8000/docs` and try `POST /rag/ask` with body:
```json
{
  "query": "What do the guidelines say about adverse events?"
}
```
- If no relevant docs are found, the API responds with a fallback message and empty sources.

## How it works
- `rag/retrieval/rag_pipeline.py` builds a Chroma vector store from `rag/vectorstore` and wires it to `ChatOpenAI` with a simple context-aware prompt.
- `rag/api/main.py` exposes `/rag/ask`, returning both the generated answer and the sources used.

## Notes
- If you see a Chroma deprecation warning, upgrade to `langchain-chroma` per the warning text.
- Ensure `rag/vectorstore` contains embeddings for your documents; rebuild as needed using your ingestion workflow.
