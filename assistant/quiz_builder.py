def build_quiz_prompt(
    context: str,
    number_of_questions: int = 5,
) -> str:
    if not context.strip():
        raise ValueError("Context cannot be empty.")

    if number_of_questions < 1:
        raise ValueError("Number of questions must be at least 1.")

    return f"""
You are PaperIQ, an AI research assistant.

Create exactly {number_of_questions} multiple-choice questions using ONLY the provided context.

Return valid JSON only.

Required format:

{{
  "quiz": [
    {{
      "question": "Question text",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "correct_answer": "Option A",
      "explanation": "Brief explanation based on the document."
    }}
  ]
}}

Rules:
- Each question must have exactly four options.
- Only one option must be correct.
- Do not use outside knowledge.
- Do not include markdown code fences.
- Do not include text before or after the JSON.
- Keep explanations concise.

Context:
{context}
""".strip()