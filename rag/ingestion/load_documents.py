# ruff: noqa: E402
from pathlib import Path
import sys

# Ensure project root on path for imports when running as a script
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_and_split_pdfs(pdf_dir="rag/data/pdfs"):
    documents = []
    for pdf in Path(pdf_dir).glob("*.pdf"):
        loader = PyPDFLoader(str(pdf))
        documents.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
    )
    return splitter.split_documents(documents)


if __name__ == "__main__":
    chunks = load_and_split_pdfs()
    print(f"Created {len(chunks)} chunks")
