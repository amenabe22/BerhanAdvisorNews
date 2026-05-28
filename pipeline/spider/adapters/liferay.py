from __future__ import annotations

from urllib.parse import urljoin, urlparse

from pipeline.db.models.sources import Source
from pipeline.spider.adapters.base import SpiderAdapter
from pipeline.spider.http import SpiderHttp
from pipeline.spider.links import extract_links
from pipeline.spider.robots import RobotsChecker


class LiferayAdapter(SpiderAdapter):
    """MOR Liferay portal — HTML link discovery with robots enforcement."""

    SEED_PATHS = (
        "/",
        "/en/web/guest/home",
        "/documents",
        "/en/documents",
        "/directives",
        "/en/directives",
    )

    def __init__(self, http: SpiderHttp, robots: RobotsChecker) -> None:
        self._http = http
        self._robots = robots

    async def discover_urls(self, source: Source) -> list[str]:
        selectors = source.selectors or {}
        bases = [source.url.rstrip("/")]
        if alt := selectors.get("alternate_base_url"):
            bases.append(alt.rstrip("/"))

        allowed_hosts: set[str] = set()
        for base in bases:
            host = urlparse(base).netloc.lower().removeprefix("www.")
            allowed_hosts.add(host)

        seed_paths = selectors.get("seed_paths") or self.SEED_PATHS
        urls: list[str] = []

        for base in bases:
            for path in seed_paths:
                page_url = urljoin(base + "/", path.lstrip("/"))
                if not await self._robots.can_fetch(page_url):
                    continue
                try:
                    response = await self._http.get(page_url)
                    links = extract_links(
                        response.text, page_url, allowed_hosts=allowed_hosts
                    )
                    # Prefer document-like paths on MOR
                    doc_links = [
                        link
                        for link in links
                        if any(
                            part in urlparse(link).path.lower()
                            for part in (
                                "/documents/",
                                "/document/",
                                "/download/",
                                "/en/",
                                "/web/",
                            )
                        )
                    ]
                    urls.extend(doc_links or links)
                except Exception:
                    continue

        return list(dict.fromkeys(urls))
