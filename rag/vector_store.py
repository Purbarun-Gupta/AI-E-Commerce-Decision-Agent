from pathlib import Path

from langchain_chroma import Chroma

from loader import load_documents, split_documents
from embeddings import embeddings


BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "chroma_db"


def create_vector_store():

    print("Loading documents...")

    documents = load_documents()

    print(f"Loaded {len(documents)} pages")

    chunks = split_documents(documents)

    print(f"Created {len(chunks)} chunks")

    print("Creating ChromaDB vector store...")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name="ecommerce_knowledge"
    )

    print("ChromaDB created successfully!")
    print(f"Stored at: {CHROMA_DIR}")

    return vector_store


if __name__ == "__main__":
    create_vector_store()