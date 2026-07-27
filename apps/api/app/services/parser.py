import csv
import io
from pathlib import Path

from docx import Document
import fitz

def parse_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8")


def parse_pdf(file_bytes: bytes) -> str:
    text_parts: list[str] = []

    with fitz.open(stream=file_bytes, filetype="pdf") as document:
        for page in document:
            page_text = page.get_text("text").strip()

            if page_text:
                text_parts.append(page_text)

    return "\n\n".join(text_parts)

def parse_docx(file_bytes: bytes) -> str:
    document = Document(io.BytesIO(file_bytes))
    text_parts: list[str] = []

    for item in document.iter_inner_content():
        if hasattr(item, "text"):
            text = item.text.strip()

            if text:
                text_parts.append(text)

    return "\n\n".join(text_parts)

def parse_csv(file_bytes: bytes) -> str:
    text = file_bytes.decode("utf-8")

    reader = csv.reader(io.StringIO(text))

    rows = []

    for row in reader:
        rows.append(" | ".join(row))

    return "\n".join(rows)


def parse_document(
    file_bytes: bytes,
    filename: str,
) -> str:
    extension = Path(filename).suffix.lower()

    if extension == ".txt":
        return parse_txt(file_bytes)
    
    if extension == ".md":
        return parse_txt(file_bytes)

    if extension == ".pdf":
        return parse_pdf(file_bytes)

    if extension == ".docx":
        return parse_docx(file_bytes)

    if extension == ".csv":
        return parse_csv(file_bytes)

    raise ValueError(f"Unsupported file type: {extension}")