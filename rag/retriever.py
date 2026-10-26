
from pathlib import Path
from langchain_chroma import Chroma
from rag.embeddings import embeddings

BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "chroma_db"

print(f"[RAG DEBUG] Retriever file: {Path(__file__).resolve()}", flush=True)
print(f"[RAG DEBUG] Database path: {CHROMA_DIR}", flush=True)

vector_store = Chroma(
    persist_directory=str(CHROMA_DIR),
    embedding_function=embeddings,
    collection_name="ecommerce_knowledge",
)

def retrieve_documents(query, k=4):
    count = vector_store._collection.count()
    print(f"[RAG DEBUG] Indexed chunks: {count}", flush=True)

    if count == 0:
        return []

    results = vector_store.similarity_search(query, k=k)
    print(f"[RAG DEBUG] Retrieved {len(results)} documents", flush=True)
    return results
