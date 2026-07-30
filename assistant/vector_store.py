import os

from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is missing.")

if not PINECONE_INDEX_NAME:
    raise ValueError("PINECONE_INDEX_NAME is missing.")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)


def retrieve_chunks(
    query_embedding: list[float],
    document_id: str,
    top_k: int = 5,
) -> list[dict]:
    if not query_embedding:
        raise ValueError("Query embedding cannot be empty.")

    if not document_id.strip():
        raise ValueError("Document ID cannot be empty.")

    response = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter={
            "document_id": {
                "$eq": document_id
            }
        },
    )

    matches = []

    for match in response.matches:
        matches.append(
            {
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata or {},
            }
        )

    return matches