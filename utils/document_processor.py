import PyPDF2
import docx

from config.config import CHUNK_SIZE, CHUNK_OVERLAP


def extract_text_from_pdf(file):
    """Extract text content from a PDF file."""
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")


def extract_text_from_docx(file):
    """Extract text content from a DOCX file."""
    try:
        doc = docx.Document(file)
        text = "\n".join(
            para.text for para in doc.paragraphs if para.text.strip()
        )
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from DOCX: {e}")


def extract_text_from_txt(file):
    """Extract text content from a plain text file."""
    try:
        return file.read().decode("utf-8").strip()
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from TXT: {e}")


def extract_text(file, filename):
    """Route file to the appropriate text extractor based on extension."""
    ext = filename.lower().rsplit(".", 1)[-1]
    extractors = {
        "pdf": extract_text_from_pdf,
        "docx": extract_text_from_docx,
        "txt": extract_text_from_txt,
    }
    if ext not in extractors:
        raise ValueError(f"Unsupported file format: .{ext}. Supported: PDF, DOCX, TXT")
    return extractors[ext](file)


def chunk_text(text, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks by word count."""
    if not text:
        return []

    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - chunk_overlap

    return chunks
