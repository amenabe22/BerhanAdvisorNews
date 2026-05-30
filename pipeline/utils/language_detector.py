"""Language detection utilities for crawler extraction."""

from __future__ import annotations

from lingua import Language, LanguageDetectorBuilder

ETHIOPIC_START = 0x1200
ETHIOPIC_END = 0x137F

_detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH,
    Language.SOMALI,
).build()

_LANG_MAP = {
    Language.ENGLISH: "en",
    Language.SOMALI: "so",
}


def detect_language(text: str) -> str:
    sample = (text or "").strip()
    if not sample:
        return "en"

    ethiopic_chars = sum(
        1 for c in sample if ETHIOPIC_START <= ord(c) <= ETHIOPIC_END
    )
    if ethiopic_chars / max(len(sample), 1) > 0.10:
        return "am"

    language = _detector.detect_language_of(sample)
    return _LANG_MAP.get(language, "en")
