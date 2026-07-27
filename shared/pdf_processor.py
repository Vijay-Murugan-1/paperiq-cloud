import fitz


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract all text from a PDF.

    Args:
        pdf_bytes: Raw PDF file content.

    Returns:
        Extracted document text.
    """

    document = fitz.open(stream=pdf_bytes, filetype="pdf")

    try:
        text = ""

        for page in document:
            text += page.get_text("text") + "\n"

    finally:
        document.close()

    return text.strip()