from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse


@dataclass(frozen=True)
class PairCandidate:
    url: str
    title: str
    published_at: datetime | None


def looks_bilingual_nbe_pair(a: PairCandidate, b: PairCandidate) -> bool:
    return _has_ethiopic(a.title) != _has_ethiopic(b.title)


def looks_bilingual_moj_pair(a: PairCandidate, b: PairCandidate) -> bool:
    pa = urlparse(a.url).path
    pb = urlparse(b.url).path
    return ("/en/newsroom/" in pa and "/am/newsroom/" in pb) or (
        "/am/newsroom/" in pa and "/en/newsroom/" in pb
    )


def looks_bilingual_mof_pair(a: PairCandidate, b: PairCandidate) -> bool:
    if not a.published_at or not b.published_at:
        return False
    if a.published_at.date() != b.published_at.date():
        return False
    return _title_similarity(a.title, b.title) >= 0.8


def _has_ethiopic(text: str) -> bool:
    return any(0x1200 <= ord(c) <= 0x137F for c in text or "")


def _title_similarity(a: str, b: str) -> float:
    words_a = set((a or "").lower().split())
    words_b = set((b or "").lower().split())
    if not words_a or not words_b:
        return 0.0
    inter = len(words_a & words_b)
    union = len(words_a | words_b)
    return inter / union
