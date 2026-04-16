from app.services.gemini_service import GeminiService


def chunk_text(text: str, max_chars: int = 10000) -> list[str]:
    chunks: list[str] = []
    current = []
    current_len = 0

    for paragraph in text.split("\n\n"):
        part = paragraph.strip()
        if not part:
            continue

        incoming_len = len(part) + 2
        if current_len + incoming_len > max_chars and current:
            chunks.append("\n\n".join(current))
            current = [part]
            current_len = len(part)
        else:
            current.append(part)
            current_len += incoming_len

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def translate_document(text: str, source_language: str) -> str:
    translator = GeminiService()
    parts = chunk_text(text)
    translated_parts: list[str] = []

    for part in parts:
        translated_parts.append(
            translator.translate_to_english(part, source_language)
        )

    return "\n\n".join(translated_parts)
