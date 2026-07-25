import os
from google import genai

# Read API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing.")

# Initialize the Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "text-embedding-004"


def generate_embedding(text: str) -> list[float]:
    """
    Generate one embedding vector.
    """
    if not text.strip():
        raise ValueError("Text is empty.")

    response = client.models.embed_content(
        model=MODEL_NAME,
        contents=text,
    )
    return response.embeddings[0].values


def generate_embeddings(chunks: list[str]) -> list[list[float]]:
    """
    Generate embeddings for multiple chunks.
    """
    if not chunks:
        raise ValueError("No chunks provided.")

    response = client.models.embed_content(
        model=MODEL_NAME,
        contents=chunks,
    )
    
    return [embedding.values for embedding in response.embeddings]