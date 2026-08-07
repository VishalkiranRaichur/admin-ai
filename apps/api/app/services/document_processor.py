from app.services.chunker import chunk_text
from app.services.embedding_service import generate_embeddings
from app.services.parser import parse_document


async def process_document(
    file_bytes: bytes,
    filename: str,
) -> dict:
    try:
        extracted_text = parse_document(
            file_bytes,
            filename,
        )
    except Exception as error:
        raise ValueError(
            f"Failed to parse document '{filename}': {error}"
        ) from error

    chunks = chunk_text(extracted_text)

    if not chunks:
        raise ValueError(
            f"No text chunks were created for '{filename}'."
        )

    embeddings = await generate_embeddings(chunks)

    if len(chunks) != len(embeddings):
        raise ValueError(
            "The number of chunks does not match the number of embeddings."
        )

    return {
        "filename": filename,
        "character_count": len(extracted_text),
        "chunk_count": len(chunks),
        "chunks": chunks,
        "embeddings": embeddings,
    }