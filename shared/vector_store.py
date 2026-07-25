import os

from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

if not PINECONE_API_KEY or not PINECONE_INDEX_NAME:
    raise ValueError("Pinecone environment variables are missing.")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)


def upload_embeddings(
    document_id: str,
    filename: str,
    chunks: list[str],
    embeddings: list[list[float]],
    page_number: int = 1,
) -> int:
    if len(chunks) != len(embeddings):
        raise ValueError("Chunks and embeddings count do not match.")

    vectors = []

    for position, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        vectors.append(
            {
                "id": f"{document_id}-p{page_number}-chunk-{position}",
                "values": embedding,
                "metadata": {
                    "document_id": document_id,
                    "filename": filename,
                    "page_number": page_number,
                    "chunk_position": position,
                    "text": chunk,
                },
            }
        )

    index.upsert(vectors=vectors)

    return len(vectors)


def query_embeddings(
    query_embedding: list[float],
    document_id: str,
    top_k: int = 5
) -> list[dict]:
    """
    Query the Pinecone index with the given embedding vector, filtered by document_id.
    """
    response = index.query(
        vector=query_embedding,
        top_k=top_k,
        filter={"document_id": {"$eq": document_id}},
        include_metadata=True
    )
    return response.matches