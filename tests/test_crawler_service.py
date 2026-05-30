from __future__ import annotations

import pytest

from pipeline.crawler.service import CrawlRequest, crawl_url


class _FakeFetcher:
    def __init__(self, html: str) -> None:
        self._html = html

    async def fetch_text(self, url: str) -> tuple[str, str]:
        return self._html, url


@pytest.mark.anyio
async def test_crawl_url_uses_source_extractor_and_detects_language():
    html = """
    <html><body>
      <h1 class="entry-title">Directive title</h1>
      <div class="elementor-widget-text-editor"><p>National Bank update.</p></div>
    </body></html>
    """
    req = CrawlRequest(
        source_code="NBE",
        source_url="https://nbe.gov.et",
        url="https://nbe.gov.et/files/fxd-04-2026/",
        link_metadata={"directive_type_code": "FXD", "directive_number": "04"},
    )

    out = await crawl_url(req, _FakeFetcher(html))
    assert out.extractor == "nbe"
    assert out.used_shadow is False
    assert out.content.language == "en"
    assert out.content.directive_number == "04"


@pytest.mark.anyio
async def test_crawl_url_falls_back_to_shadow_when_extractor_empty():
    html = "<html><head><title>Fallback Title</title></head><body></body></html>"
    req = CrawlRequest(
        source_code="MOJ",
        source_url="https://justice.gov.et",
        url="https://justice.gov.et/en/newsroom/some-page/",
        link_metadata={},
    )

    out = await crawl_url(req, _FakeFetcher(html))
    assert out.used_shadow is True
    assert out.extractor == "shadow"
    assert out.content.title == "Fallback Title"
