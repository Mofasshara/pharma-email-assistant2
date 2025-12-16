from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA


def build_vectorstore(pdf_path="sample.pdf"):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    db = Chroma.from_documents(
        docs, OpenAIEmbeddings()
    )
    return db