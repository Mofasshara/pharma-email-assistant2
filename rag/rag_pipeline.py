from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


def build_vectorstore(pdf_path="sample.pdf"):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    db = Chroma.from_documents(
        docs, OpenAIEmbeddings()
    )
    return db
