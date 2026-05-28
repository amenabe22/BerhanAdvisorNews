from __future__ import annotations

from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET

from pipeline.db.models.sources import Source
from pipeline.spider.adapters.base import SpiderAdapter
from pipeline.spider.http import SpiderHttp
from pipeline.spider.links import filter_by_patterns
from pipeline.spider.robots import RobotsChecker

SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


class SitemapAdapter(SpiderAdapter):
    def __init__(self, http: SpiderHttp, robots: RobotsChecker) -> None:
        self._http = http
        self._robots = robots

    async def discover_urls(self, source: Source) -> list[str]:
        selectors = source.selectors or {}
        sitemap_url = selectors.get("sitemap_url") or urljoin(
            source.url.rstrip("/") + "/", "sitemap.xml"
        )
        # WordPress often redirects sitemap.xml -> wp-sitemap.xml
        extra = selectors.get("sitemap_urls") or []
        sitemap_candidates = list(dict.fromkeys([sitemap_url, *extra]))

        urls: list[str] = []
        for candidate in sitemap_candidates:
            if not await self._robots.can_fetch(candidate):
                continue
            urls.extend(await self._collect_from_sitemap(candidate))
        patterns = [
            selectors.get("article_url_pattern"),
            selectors.get("directive_url_pattern"),
        ]
        patterns = [p for p in patterns if p]
        if patterns:
            urls = filter_by_patterns(urls, patterns)
        return list(dict.fromkeys(urls))

    async def _collect_from_sitemap(self, sitemap_url: str, depth: int = 0) -> list[str]:
        if depth > 5:
            return []

        try:
            response = await self._http.get(sitemap_url)
            root = ET.fromstring(response.content)
        except Exception:
            return []

        tag = _local_name(root.tag)
        if tag == "sitemapindex":
            child_urls: list[str] = []
            for loc in root.findall(".//sm:loc", SITEMAP_NS):
                if loc.text:
                    child_urls.extend(
                        await self._collect_from_sitemap(loc.text.strip(), depth + 1)
                    )
            return child_urls

        if tag == "urlset":
            found: list[str] = []
            for loc in root.findall(".//sm:loc", SITEMAP_NS):
                if not loc.text:
                    continue
                page_url = loc.text.strip()
                if await self._robots.can_fetch(page_url):
                    found.append(page_url)
            return found

        return []


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag
