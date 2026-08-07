DEFAULT_CHUNK_SIZE = 1200
DEFAULT_CHUNK_OVERLAP = 200


def _find_split_position(
    text: str,
    start: int,
    target_end: int,
) -> int:
    if target_end >= len(text):
        return len(text)

    search_start = max(start, target_end - 300)
    window = text[search_start:target_end]

    separators = [
        "\n\n",
        ". ",
        "? ",
        "! ",
        "\n",
        " ",
    ]

    for separator in separators:
        position = window.rfind(separator)

        if position != -1:
            return search_start + position + len(separator)

    return target_end


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    cleaned_text = text.strip()

    if not cleaned_text:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(cleaned_text):
        target_end = min(start + chunk_size, len(cleaned_text))
        end = _find_split_position(
            cleaned_text,
            start,
            target_end,
        )

        chunk = cleaned_text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(cleaned_text):
            break

        next_start = max(end - chunk_overlap, start + 1)
        start = next_start

    return chunks