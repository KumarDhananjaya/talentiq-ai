from pathlib import Path

from pypdf import PdfReader


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF resume.

    Args:
        file_path: Path to the uploaded PDF.

    Returns:
        Extracted text from all PDF pages.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Resume file not found: {file_path}"
        )

    reader = PdfReader(path)

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages).strip()