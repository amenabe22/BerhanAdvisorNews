"""Unit tests for spider URL utilities."""

from pipeline.utils.directive_meta import extract_directive_meta
from pipeline.utils.url_normalizer import normalize_url, url_hash


def test_normalize_strips_utm_and_www():
    raw = "https://www.example.com/path/?utm_source=fb&id=1#section"
    assert normalize_url(raw) == "https://example.com/path?id=1"


def test_normalize_ethiopic_slug_decode():
    path = "/blog/%E1%8B%A8%E1%8C%88%E1%8A%95%E1%8B%98%E1%89%A5/"
    url = f"https://www.mofed.gov.et{path}"
    normalized = normalize_url(url)
    assert "%E1" not in normalized
    assert "mofed.gov.et" in normalized


def test_url_hash_stable():
    a = url_hash("https://example.com/a")
    b = url_hash("https://example.com/a")
    assert a == b
    assert len(a) == 64


def test_directive_meta_nbe_slugs():
    cases = [
        ("/files/fxd-04-2026/", "FXD", "04", 2026),
        ("/files/sib-62-2026/", "SIB", "62", 2026),
        ("/files/nbe-int-13-2026/", "NBE_INT", "13", 2026),
    ]
    for path, code, num, year in cases:
        meta = extract_directive_meta(path)
        assert meta is not None
        assert meta["directive_type_code"] == code
        assert meta["directive_number"] == num
        assert meta["directive_year"] == year


def test_directive_meta_non_match():
    assert extract_directive_meta("/nbe_news/some-article/") is None
