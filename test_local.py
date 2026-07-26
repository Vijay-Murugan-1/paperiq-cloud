import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("--- Step 1: Checking Environment Variables ---")
gemini_key = os.getenv("GEMINI_API_KEY")
pinecone_key = os.getenv("PINECONE_API_KEY")
pinecone_index = os.getenv("PINECONE_INDEX_NAME")

print(f"Gemini Key Loaded: {bool(gemini_key)}")
print(f"Pinecone Key Loaded: {bool(pinecone_key)}")
print(f"Index Name: {pinecone_index}")

if not all([gemini_key, pinecone_key, pinecone_index]):
    print("Error: Missing keys in .env file.")
    sys.exit(1)

print("\n--- Step 2: Testing Pinecone Connection ---")
try:
    from pinecone import Pinecone
    pc = Pinecone(api_key=pinecone_key)
    index_list = [idx.name for idx in pc.list_indexes()]
    print(f"Successfully connected to Pinecone! Indexes: {index_list}")
    
    if pinecone_index not in index_list:
        print(f"Warning: Index '{pinecone_index}' not found in your Pinecone account.")
except Exception as e:
    print(f"Pinecone Error: {e}")

print("\n--- Step 3: Testing Google Gemini Connection ---")
try:
    from google import genai
    client = genai.Client(api_key=gemini_key)
    
    # Try text-embedding-004 or fallback to gemini-embedding-001
    embedding_model = "text-embedding-004"
    try:
        response = client.models.embed_content(
            model=embedding_model,
            contents="Testing PaperIQ setup",
        )
    except Exception:
        embedding_model = "gemini-embedding-001"
        response = client.models.embed_content(
            model=embedding_model,
            contents="Testing PaperIQ setup",
        )

    # Handle embedding response structure
    emb_values = getattr(response, 'embedding', None)
    if hasattr(emb_values, 'values'):
        length = len(emb_values.values)
    elif isinstance(emb_values, list):
        length = len(emb_values)
    else:
        length = "Unknown"

    print(f"Successfully connected to Gemini API using [{embedding_model}]! Vector length: {length}")
except Exception as e:
    print(f"Gemini Error: {e}")