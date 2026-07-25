import pypdf

def process_pdf(file_path: str) -> list[dict]:
    """
    Reads a PDF file and extracts text cleanly.
    Returns a list of dictionaries containing page-numbered text blocks.
    """
    blocks = []
    with open(file_path, "rb") as f:
        reader = pypdf.PdfReader(f)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                text = text.strip()
                if text:
                    blocks.append({
                        "page_number": i + 1,
                        "text": text
                    })
    return blocks
