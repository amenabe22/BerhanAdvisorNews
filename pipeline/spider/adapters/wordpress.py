from __future__ import annotations

from urllib.parse import urljoin

from pipeline.db.models.sources import Source
from pipeline.spider.adapters.base import SpiderAdapter
from pipeline.spider.http import SpiderHttp
from pipeline.spider.links import extract_links, filter_by_patterns
from pipeline.spider.robots import RobotsChecker


class WordPressAdapter(SpiderAdapter):
    """WordPress sites: REST API + listing page fallback (NBE)."""

    def __init__(self, http: SpiderHttp, robots: RobotsChecker) -> None:
        self._http = http
        self._robots = robots

    async def discover_urls(self, source: Source) -> list[str]:
        selectors = source.selectors or {}
        urls: list[str] = []

        post_type = selectors.get("wp_post_type", "nbe_news")
        api_urls = await self._fetch_wp_api(source, post_type)
        urls.extend(api_urls)

        listing_paths = [
            selectors.get("news_listing"),
            selectors.get("archive_listing"),
            selectors.get("directives_listing"),
        ]
        patterns = [
            selectors.get("article_url_pattern"),
            selectors.get("directive_url_pattern"),
        ]

        for path in listing_paths:
            if not path:
                continue
            listing_urls = await self._crawl_listing_page(source, path, patterns)
            urls.extend(listing_urls)

        return list(dict.fromkeys(urls))

    async def _fetch_wp_api(self, source: Source, post_type: str) -> list[str]:
        base = source.url.rstrip("/")
        endpoint = f"{base}/wp-json/wp/v2/{post_type}"
        found: list[str] = []
        page = 1

        while page <= 20:
            api_url = f"{endpoint}?per_page=100&page={page}"
            if not await self._robots.can_fetch(api_url):
                break
            try:
                response = await self._http.get(api_url)
                if response.status_code == 404:
                    break
                data = response.json()
            except Exception:
                break

            if not isinstance(data, list) or not data:
                break

            for item in data:
                link = item.get("link")
                if link and await self._robots.can_fetch(link):
                    found.append(link)

            if len(data) < 100:
                break
            page += 1

        return found

    async def _crawl_listing_page(
        self,
        source: Source,
        path: str,
        patterns: list[str | None],
    ) -> list[str]:
        listing_url = urljoin(source.url.rstrip("/") + "/", path.lstrip("/"))
        if not await self._robots.can_fetch(listing_url):
            return []
        try:
            response = await self._http.get(listing_url)
            host = source.url.split("//", 1)[-1].split("/")[0].lower().removeprefix("www.")
            allowed = {host}
            links = extract_links(response.text, listing_url, allowed_hosts=allowed)
            clean_patterns = [p for p in patterns if p]
            if clean_patterns:
                links = filter_by_patterns(links, clean_patterns)
            return links
        except Exception:
            return []
