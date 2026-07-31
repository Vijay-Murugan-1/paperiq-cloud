import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing.")

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-embedding-2"


def generate_embedding(text: str) -> list[float]:
    """
    Generate one embedding vector for a given piece of text.
    """
    # Guard against empty/whitespace string errors
    text_content = text if text.strip() else "empty chunk"

    response = client.models.embed_content(
        model=MODEL_NAME,
        contents=text_content,
        config=types.EmbedContentConfig(output_dimensionality=768)
    )
    return response.embeddings[0].values


def generate_embeddings(chunks: list[str]) -> list[list[float]]:
    """
    Generate embeddings 1-by-1 to guarantee a 1-to-1 match count with chunks.
    """
    if not chunks:
        raise ValueError("No chunks provided.")

    embeddings = []
    for chunk in chunks:
        vec = generate_embedding(chunk)
        embeddings.append(vec)

    return embeddings