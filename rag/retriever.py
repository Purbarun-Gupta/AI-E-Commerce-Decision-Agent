from pathlib import Path

from langchain_chroma import Chroma

from rag.embeddings import embeddings


BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "chroma_db"


vector_store = Chroma(
    persist_directory=str(CHROMA_DIR),
    embedding_function=embeddings,
    collection_name="ecommerce_knowledge"
)


def retrieve_documents(query, k=4):
    results = vector_store.similarity_search(
        query,
        k=k
    )

    return results


if __name__ == "__main__":

    query = "What is the cancellation and return policy?"

    results = retrieve_documents(query)

    print(f"\nRetrieved {len(results)} documents\n")

    for i, doc in enumerate(results, start=1):

        print("=" * 70)
        print(f"RESULT {i}")

        print("\nSource:")
        print(doc.metadata.get("source"))

        print("\nPage:")
        print(doc.metadata.get("page"))

        print("\nContent:")
        print(doc.page_content[:1000])