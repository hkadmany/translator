from deep_translator import GoogleTranslator


def translate_segments(segments: list[dict]) -> list[dict]:
    """Translate English text segments to Arabic.

    Takes and returns list of dicts with keys: start, end, text
    """
    translator = GoogleTranslator(source="en", target="ar")
    translated = []
    for seg in segments:
        arabic_text = translator.translate(seg["text"])
        translated.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": arabic_text,
        })
    return translated
