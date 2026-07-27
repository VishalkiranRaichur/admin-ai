from app.services.chunker import chunk_text
from app.services.parser import parse_document


def process_document(
    file_bytes: bytes,
    filename: str,
) -> dict:
    try:
        extracted_text = parse_document(file_bytes, filename)
    except Exception as error:
        raise ValueError(
            f"Failed to parse document '{filename}': {error}"
        ) from error

    chunks = chunk_text(extracted_text)

    return {
        "filename": filename,
        "character_count": len(extracted_text),
        "chunk_count": len(chunks),
        "chunks": chunks,
    }