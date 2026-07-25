def build_flashcard_prompt(
    context: str,
    number_of_flashcards: int = 5,
) -> str:
    if not context.strip():
        raise ValueError("Context cannot be empty.")

    if number_of_flashcards < 1:
        raise ValueError("Number of flashcards must be at least 1.")

    return f"""
You are PaperIQ, an AI research assistant.

Create exactly {number_of_flashcards} flashcards using ONLY the provided context.

Return valid JSON only.

Required format:

{{
  "flashcards": [
    {{
      "question": "Flashcard question",
      "answer": "Concise answer"
    }}
  ]
}}

Rules:
- Do not use outside knowledge.
- Keep each answer concise and factual.
- Do not include markdown code fences.
- Do not include text before or after the JSON.

Context:
{context}
""".strip()