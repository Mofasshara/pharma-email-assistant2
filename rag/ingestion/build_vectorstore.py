from pathlib import Path
import sys

# Ensure project root on path for imports when running as a script
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from rag.ingestion.load_documents import load_and_split_pdfs
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


def build_vectorstore():
    chunks = load_and_split_pdfs()
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="rag/vectorstore",
    )
    vectordb.persist()
    print("Vector store built")


if __name__ == "__main__":
    build_vectorstore()
