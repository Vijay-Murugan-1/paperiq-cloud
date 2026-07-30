from transformers import AutoTokenizer


TOKENIZER_NAME = "BAAI/bge-small-en-v1.5"
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME)


def create_chunks(
    text: str,
    chunk_size: int = 512,
    overlap: int = 50,
) -> list[str]:
    if not text.strip():
        raise ValueError("Document text is empty.")

    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")

    tokens = tokenizer.encode(
        text,
        add_special_tokens=False,
        truncation=False,
    )

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(tokens), step):
        chunk_tokens = tokens[start:start + chunk_size]

        if not chunk_tokens:
            continue

        chunk_text = tokenizer.decode(
            chunk_tokens,
            skip_special_tokens=True,
        ).strip()

        if chunk_text:
            chunks.appendnext(chunk_text)

    return chunks