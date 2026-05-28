from __future__ import annotations

from urllib.parse import urljoin, urlparse

from pipeline.db.models.sources import Source
from pipeline.spider.adapters.base import SpiderAdapter
from pipeline.spider.http import SpiderHttp
from pipeline.spider.links import extract_links, filter_by_patterns
from pipeline.spider.robots import RobotsChecker


class FIRMAAdapter(SpiderAdapter):
    """MOJ FIRMA CMS — newsroom listing with retries."""

    MAX_RETRIES = 5

    def __init__(self, http: SpiderHttp, robots: RobotsChecker) -> None:
        self._http = http
        self._robots = robots

    async def discover_urls(self, source: Source) -> list[str]:
        selectors = source.selectors or {}
        max_retries = int(selectors.get("max_retries", self.MAX_RETRIES))
        listing_path = selectors.get("news_listing", "/en/newsroom/")
        listing_url = urljoin(source.url.rstrip("/") + "/", listing_path.lstrip("/"))

        if not await self._robots.can_fetch(listing_url):
            return _fallback_urls(selectors)

        html: str | None = None
        for attempt in range(max_retries):
            try:
                response = await self._http.get(listing_url)
                html = response.text
                break
            except Exception:
                if attempt == max_retries - 1:
                    return []
                continue

        if not html:
            return _fallback_urls(selectors)

        if "bot verification" in html.lower() or "captcha" in html.lower():
            return _fallback_urls(selectors)

        host = urlparse(source.url).netloc.lower().removeprefix("www.")
        links = extract_links(html, listing_url, allowed_hosts={host})

        patterns = [selectors.get("article_url_pattern", "/en/newsroom/")]
        if patterns[0]:
            links = filter_by_patterns(links, patterns) or links

        # Also discover /am/ mirror listings
        am_listing = listing_url.replace("/en/", "/am/", 1)
        if am_listing != listing_url and await self._robots.can_fetch(am_listing):
            try:
                am_response = await self._http.get(am_listing)
                am_links = extract_links(am_response.text, am_listing, allowed_hosts={host})
                links.extend(am_links)
            except Exception:
                pass

        if not links:
            return _fallback_urls(selectors)

        return list(dict.fromkeys(links))


def _fallback_urls(selectors: dict) -> list[str]:
    """MOJ often serves a bot wall; use configured seed/canary URLs."""
    seeds = selectors.get("seed_urls") or selectors.get("canary_urls") or []
    return list(dict.fromkeys(u for u in seeds if u))
