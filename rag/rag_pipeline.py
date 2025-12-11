from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma


def build_vectorstore(pdf_path="sample.pdf"):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    db = Chroma.from_documents(
        docs, OpenAIEmbeddings()
    )
    return db