import warnings

with warnings.catch_warnings():
    warnings.filterwarnings(
        "ignore",
        message=".*google\\.generativeai.*",
        category=FutureWarning,
    )
    import google.generativeai as genai

from app.config import settings


class GeminiService:
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)

    def translate_to_english(self, source_text: str, source_language: str) -> str:
        prompt = f"""
You are a precise language translator.
Translate the given document content to natural and accurate English.
Preserve headings, numbering, bullet points, and meaning.
Do not add explanations.

Source language hint: {source_language}

Document text:
{source_text}
""".strip()

        response = self.model.generate_content(prompt)
        translated = (response.text or "").strip()
        if not translated:
            raise ValueError("Gemini returned empty translation output.")
        return translated
