import sys
from pathlib import Path

FLASK_SERVER_DIR = Path(__file__).resolve().parent.parent / "flask-server"

sys.path.insert(0, str(FLASK_SERVER_DIR))

from rag.retriever import retrieve_documents
from ai.gemini import generate_response


def ask_rag(question, k=4):

    # 1. Retrieve relevant documents
    documents = retrieve_documents(question, k=k)

    if not documents:
        return "I could not find relevant information in the knowledge base."

    # 2. Build context
    context_parts = []

    for doc in documents:

        source = doc.metadata.get("source", "Unknown source")
        page = doc.metadata.get("page", "Unknown page")

        context_parts.append(
            f"""
SOURCE: {source}
PAGE: {page}

CONTENT:
{doc.page_content}
"""
        )

    context = "\n\n".join(context_parts)

    # 3. Send retrieved context to Gemini
    prompt = f"""
You are an e-commerce business assistant.

Answer the user's question using ONLY the provided
knowledge base context.

If the answer is not present in the context,
say that the information was not found in the
knowledge base.

Do not invent policies, rules, dates, or conditions.

USER QUESTION:
{question}

KNOWLEDGE BASE CONTEXT:
{context}

Provide a clear and concise answer.
"""

    answer = generate_response(prompt)

    return {
        "question": question,
        "answer": answer,
        "sources": [
            {
                "source": doc.metadata.get("source"),
                "page": doc.metadata.get("page")
            }
            for doc in documents
        ]
    }


if __name__ == "__main__":

    question = "Can I cancel my order after it has been dispatched?"

    result = ask_rag(question)

    print("\nQUESTION:")
    print(result["question"])

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")

    for source in result["sources"]:
        print(
            f"- {source['source']} "
            f"(page {source['page']})"
        )