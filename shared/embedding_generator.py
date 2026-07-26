import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


# Read API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing.")

# Initialize the Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-embedding-2"


def generate_embedding(text: str) -> list[float]:
    """
    Generate one embedding vector.
    """
    if not text.strip():
        raise ValueError("Text is empty.")

    response = client.models.embed_content(
        model=MODEL_NAME,
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=768)
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
        config=types.EmbedContentConfig(output_dimensionality=768)
    )
    
    return [embedding.values for embedding in response.embeddings]