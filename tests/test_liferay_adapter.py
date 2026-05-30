from __future__ import annotations

from types import SimpleNamespace

import pytest

from pipeline.spider.adapters.liferay import LiferayAdapter


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class _FakeHttp:
    def __init__(self, html: str) -> None:
        self._html = html

    async def get(self, _url: str) -> _FakeResponse:
        return _FakeResponse(self._html)


class _AllowAllRobots:
    async def can_fetch(self, _url: str) -> bool:
        return True


@pytest.mark.anyio
async def test_liferay_falls_back_to_canary_urls_when_no_links_found():
    source = SimpleNamespace(
        url="https://www.mor.gov.et",
        selectors={
            "seed_paths": ["/en/directives"],
            "canary_urls": ["https://www.mor.gov.et/"],
        },
    )
    adapter = LiferayAdapter(_FakeHttp("<html><body>No links here</body></html>"), _AllowAllRobots())

    urls = await adapter.discover_urls(source)

    assert urls == ["https://www.mor.gov.et/"]


@pytest.mark.anyio
async def test_liferay_prefers_discovered_links_when_available():
    source = SimpleNamespace(
        url="https://www.mor.gov.et",
        selectors={
            "seed_paths": ["/en/directives"],
            "canary_urls": ["https://www.mor.gov.et/"],
        },
    )
    html = '<a href="/documents/sample.pdf">Doc</a>'
    adapter = LiferayAdapter(_FakeHttp(html), _AllowAllRobots())

    urls = await adapter.discover_urls(source)

    assert "https://www.mor.gov.et/documents/sample.pdf" in urls
