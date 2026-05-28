from __future__ import annotations

from urllib.parse import urljoin, urlparse

from pipeline.db.models.sources import Source
from pipeline.spider.adapters.base import SpiderAdapter
from pipeline.spider.http import SpiderHttp
from pipeline.spider.links import extract_links, filter_by_patterns
from pipeline.spider.robots import RobotsChecker


class ListingAdapter(SpiderAdapter):
    """Django / generic HTML listing pages (MOF)."""

    DEFAULT_LISTINGS = (
        "/press-media/news/",
        "/mof-directive/customs-directive/",
        "/mof-directive/tax-directive/",
        "/mof-directive/circular/",
    )

    def __init__(self, http: SpiderHttp, robots: RobotsChecker) -> None:
        self._http = http
        self._robots = robots

    async def discover_urls(self, source: Source) -> list[str]:
        selectors = source.selectors or {}
        paths = selectors.get("listing_paths") or [
            selectors.get("news_listing"),
            selectors.get("directives_base"),
            *self.DEFAULT_LISTINGS,
        ]
        paths = list(dict.fromkeys(p for p in paths if p))

        patterns = [selectors.get("article_url_pattern")]
        pdf_pattern = selectors.get("pdf_path_pattern")
        if pdf_pattern:
            patterns.append(f"*{pdf_pattern}*")

        base_host = urlparse(source.url).netloc.lower().removeprefix("www.")
        allowed_hosts = {base_host}

        urls: list[str] = []
        for path in paths:
            listing_url = urljoin(source.url.rstrip("/") + "/", path.lstrip("/"))
            if not await self._robots.can_fetch(listing_url):
                continue
            try:
                response = await self._http.get(listing_url)
                links = extract_links(response.text, listing_url, allowed_hosts=allowed_hosts)
                article_pattern = selectors.get("article_url_pattern")
                if article_pattern:
                    links = filter_by_patterns(links, [article_pattern])
                urls.extend(links)
            except Exception:
                continue

        return list(dict.fromkeys(urls))
