import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import INDEX_PATH, PDF_PATH, SOURCES


def load_documents() -> list[Document]:
    documents: list[Document] = []
    session = requests.Session()

    for url in SOURCES:
        response = session.get(url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        documents.append(
            Document(
                page_content=soup.get_text(" ", strip=True),
                metadata={"source": url},
            )
        )

    if not PDF_PATH.is_file():
        raise FileNotFoundError(f"Source PDF not found: {PDF_PATH}")
    documents.extend(PyPDFLoader(str(PDF_PATH)).load())
    return documents


def build_index() -> None:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = splitter.split_documents(load_documents())
    if not chunks:
        raise RuntimeError("No source documents were loaded; FAISS index not built.")

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_db = FAISS.from_documents(chunks, embeddings)
    vector_db.save_local(str(INDEX_PATH))
    print(f"Saved {len(chunks)} document chunks to {INDEX_PATH}")


if __name__ == "__main__":
    build_index()
