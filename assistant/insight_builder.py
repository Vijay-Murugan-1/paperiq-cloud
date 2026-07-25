def build_insight_prompt(
    context: str,
    number_of_insights: int = 5,
) -> str:
    if not context.strip():
        raise ValueError("Context cannot be empty.")

    if number_of_insights < 1:
        raise ValueError("Number of insights must be at least 1.")

    return f"""
You are PaperIQ, an AI research assistant.

Extract exactly {number_of_insights} important insights using ONLY the provided context.

Return valid JSON only.

Required format:

{{
  "insights": [
    {{
      "title": "Short insight title",
      "description": "Clear explanation of the insight"
    }}
  ]
}}

Rules:
- Do not use outside knowledge.
- Focus on important findings, methods, contributions, or implications.
- Keep each insight concise and factual.
- Do not include markdown code fences.
- Do not include text before or after the JSON.

Context:
{context}
""".strip()