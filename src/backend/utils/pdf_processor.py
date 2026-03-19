
import pymupdf
from pathlib import Path
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"File is not a PDF: {pdf_path}")

    doc = pymupdf.open(str(path))
    full_text = []

    for page_num, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            full_text.append(text)
            logger.debug(f"Page {page_num + 1} extracted | chars={len(text)}")

    doc.close()

    result = "\n\n".join(full_text)
    logger.info(f"PDF extracted | file={path.name} | total_chars={len(result)}")
    return result


def chunk_text(text: str) -> list[str]:
    
    words = text.split()
    chunk_size = settings.chunk_size
    overlap = settings.chunk_overlap

    if not words:
        raise ValueError("Empty document: No text found to process.")

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap

    logger.info(f"Text chunked | total_words={len(words)} | chunks={len(chunks)}")
    return chunks


def process_pdf(pdf_path: str) -> list[str]:
    
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)
    return chunks