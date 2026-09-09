import hashlib
import pymupdf


def calculate_file_hash(pdf_path_or_bytes):
    """Calculate SHA-256 hash of PDF file path or raw bytes."""
    hasher = hashlib.sha256()
    if isinstance(pdf_path_or_bytes, (bytes, bytearray)):
        hasher.update(pdf_path_or_bytes)
    else:
        with open(pdf_path_or_bytes, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
    return hasher.hexdigest()


def extract_text_from_pdf(pdf_path_or_bytes):
    """Extract page-indexed text from a PDF file path or raw bytes."""
    if isinstance(pdf_path_or_bytes, (bytes, bytearray)):
        document = pymupdf.open(stream=pdf_path_or_bytes, filetype="pdf")
    else:
        document = pymupdf.open(pdf_path_or_bytes)

    pages = []

    for page_number, page in enumerate(document):
        text = page.get_text()

        pages.append({
            "page_number": page_number + 1,
            "text": text
        })

    document.close()

    return pages