from langchain_huggingface import HuggingFaceEmbeddings


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


if __name__ == "__main__":
    text = "How does the company handle product returns?"

    vector = embeddings.embed_query(text)

    print("Embedding generated successfully!")
    print("Vector length:", len(vector))
    print("First 10 values:", vector[:10])