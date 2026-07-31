import io
import pypdf

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract all text from a PDF.

    Args:
        pdf_bytes: Raw PDF file content.

    Returns:
        Extracted document text.
    """
    # pypdf requires a file-like object, so we wrap the raw bytes
    stream = io.BytesIO(pdf_bytes)
    reader = pypdf.PdfReader(stream)
    
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
            
    return text.strip()