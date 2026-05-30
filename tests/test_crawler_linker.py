from datetime import datetime

from pipeline.crawler.linker import (
    PairCandidate,
    looks_bilingual_mof_pair,
    looks_bilingual_moj_pair,
    looks_bilingual_nbe_pair,
)


def test_nbe_bilingual_pair_detection_uses_ethiopic_signal():
    en = PairCandidate(
        url="https://nbe.gov.et/nbe_news/policy-update/",
        title="Policy Update",
        published_at=datetime(2026, 5, 1),
    )
    am = PairCandidate(
        url="https://nbe.gov.et/am/nbe_news/ፖሊሲ-ማሻሻያ/",
        title="ፖሊሲ ማሻሻያ",
        published_at=datetime(2026, 5, 1),
    )
    assert looks_bilingual_nbe_pair(en, am) is True


def test_moj_bilingual_pair_detection_uses_en_am_paths():
    en = PairCandidate(
        url="https://justice.gov.et/en/newsroom/item/",
        title="Update",
        published_at=None,
    )
    am = PairCandidate(
        url="https://justice.gov.et/am/newsroom/item/",
        title="ማሻሻያ",
        published_at=None,
    )
    assert looks_bilingual_moj_pair(en, am) is True


def test_mof_bilingual_pair_detection_uses_date_and_title_similarity():
    a = PairCandidate(
        url="https://www.mofed.gov.et/blog/update-1/",
        title="Macroeconomic policy update",
        published_at=datetime(2026, 5, 1),
    )
    b = PairCandidate(
        url="https://www.mofed.gov.et/am/blog/update-1/",
        title="policy update macroeconomic",
        published_at=datetime(2026, 5, 1),
    )
    assert looks_bilingual_mof_pair(a, b) is True
