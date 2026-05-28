from __future__ import annotations

import asyncio
from urllib.parse import urljoin

import feedparser

from pipeline.db.models.sources import Source
from pipeline.spider.adapters.base import SpiderAdapter
from pipeline.spider.http import SpiderHttp
from pipeline.spider.robots import RobotsChecker


class RSSAdapter(SpiderAdapter):
    FEED_PATHS = ("/feed/", "/rss/", "/atom.xml", "/feed/rss/", "/index.xml")

    def __init__(self, http: SpiderHttp, robots: RobotsChecker) -> None:
        self._http = http
        self._robots = robots

    async def discover_urls(self, source: Source) -> list[str]:
        selectors = source.selectors or {}
        candidates: list[str] = []

        if rss_url := selectors.get("rss_url"):
            candidates.append(rss_url)
        else:
            base = source.url.rstrip("/")
            candidates.extend(urljoin(base + "/", path.lstrip("/")) for path in self.FEED_PATHS)

        urls: list[str] = []
        for feed_url in candidates:
            if not await self._robots.can_fetch(feed_url):
                continue
            found = await self._parse_feed(feed_url)
            if found:
                urls.extend(found)
                break

        return list(dict.fromkeys(urls))

    async def _parse_feed(self, feed_url: str) -> list[str]:
        try:
            response = await self._http.get(feed_url)
            parsed = await asyncio.to_thread(feedparser.parse, response.text)
        except Exception:
            return []

        links: list[str] = []
        for entry in parsed.entries:
            link = entry.get("link")
            if link and await self._robots.can_fetch(link):
                links.append(link)
        return links
