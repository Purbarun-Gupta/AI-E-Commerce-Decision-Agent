from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def load_documents():
    documents = []

    pdf_files = list(DATA_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in {DATA_DIR}"
        )

    for pdf_file in pdf_files:
        print(f"Loading: {pdf_file.name}")

        loader = PyPDFLoader(str(pdf_file))
        docs = loader.load()

        for doc in docs:
            doc.metadata["source"] = pdf_file.name

        documents.extend(docs)

    return documents


def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_documents(documents)

    return chunks


if __name__ == "__main__":
    documents = load_documents()

    print(f"\nTotal pages loaded: {len(documents)}")

    chunks = split_documents(documents)

    print(f"Total chunks created: {len(chunks)}")

    if chunks:
        print("\nSample chunk:")
        print(chunks[0].page_content[:500])

        print("\nMetadata:")
        print(chunks[0].metadata)