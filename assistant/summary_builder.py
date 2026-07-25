def build_summary_prompt(context: str) -> str:
    if not context.strip():
        raise ValueError("Context cannot be empty.")

    return f"""
You are PaperIQ, an AI research assistant.

Generate a structured summary of the document using ONLY the provided context.

Format:

# Overview
(2-3 paragraphs)

# Key Contributions
- Bullet points

# Methodology
- Bullet points

# Important Findings
- Bullet points

# Conclusion
(Short paragraph)

Rules:
- Do not add information not present in the context.
- Keep the summary factual and concise.
- If any section is not supported by the context, state "Not available in the provided document."

Context:
{context}

Summary:
""".strip()