from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

# Load environment variables (e.g., OPENAI_API_KEY) from a local .env file.
load_dotenv()


def get_rag_chain():
    vectordb = Chroma(
        persist_directory="rag/vectorstore",
        embedding_function=OpenAIEmbeddings()
    )

    retriever = vectordb.as_retriever(search_kwargs={"k": 4})

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = ChatPromptTemplate.from_template(
        "Use the following context to answer the question.\n\n"
        "Context:\n{context}\n\nQuestion: {question}"
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    # Return both the generated answer and the retrieved source documents.
    return RunnableParallel(result=rag_chain, source_documents=retriever)


if __name__ == "__main__":
    qa = get_rag_chain()
    result = qa.invoke("What does the guideline say about adverse events?")
    print(result)
