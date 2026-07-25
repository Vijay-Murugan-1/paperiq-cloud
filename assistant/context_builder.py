def build_context(matches: list[dict]) -> str:
    """
    Build a context string from Pinecone query matches.
    """

    if not matches:
        return ""

    context_parts = []

    for index, match in enumerate(matches, start=1):
        metadata = match.get("metadata", {})
        text = metadata.get("text", "").strip()
        page_number = metadata.get("page_number", "")

        if not text:
            continue

        page_str = f" (Page {page_number})" if page_number else ""
        context_parts.append(
            f"Context {index}{page_str}:\n{text}"
        )

    return "\n\n".join(context_parts)