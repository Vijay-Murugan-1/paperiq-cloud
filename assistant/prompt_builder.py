def build_qa_prompt(context: str, question: str) -> str:
    if not context.strip():
        raise ValueError("Context cannot be empty.")

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    return f"""
You are PaperIQ, an AI research assistant.

Answer the question using only the provided context.

Rules:
- Do not use outside knowledge.
- Do not invent information.
- If the answer is not present in the context, say:
  "The answer was not found in the uploaded document."
- Keep the answer clear and concise.

Context:
{context}

Question:
{question}

Answer:
""".strip()