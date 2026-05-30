"""HTTP fetcher for crawler phase (network only component)."""

from __future__ import annotations

import asyncio
import random
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx

from pipeline.spider.http import USER_AGENT


class HTTPFetcher:
    def __init__(
        self,
        *,
        max_concurrent_per_host: int = 2,
        delay_s: float = 0.5,
        jitter_s: float = 0.2,
        timeout_read_s: float = 60.0,
        verify_ssl: bool = True,
    ) -> None:
        self._delay_s = delay_s
        self._jitter_s = jitter_s
        self._max_concurrent_per_host = max_concurrent_per_host
        self._semaphores: dict[str, asyncio.Semaphore] = {}
        self._robots: dict[str, RobotFileParser | None] = {}
        self._client = httpx.AsyncClient(
            headers={"User-Agent": USER_AGENT},
            timeout=httpx.Timeout(connect=15.0, read=timeout_read_s, write=10.0, pool=5.0),
            follow_redirects=True,
            verify=verify_ssl,
        )

    async def close(self) -> None:
        await self._client.aclose()

    def _semaphore_for(self, url: str) -> asyncio.Semaphore:
        host = urlparse(url).netloc.lower() or "default"
        if host not in self._semaphores:
            self._semaphores[host] = asyncio.Semaphore(self._max_concurrent_per_host)
        return self._semaphores[host]

    async def _robots_for(self, url: str) -> RobotFileParser | None:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin in self._robots:
            return self._robots[origin]

        parser = RobotFileParser()
        robots_url = urljoin(origin + "/", "robots.txt")
        try:
            response = await self._client.get(robots_url)
            if response.status_code >= 400:
                self._robots[origin] = None
            else:
                parser.parse(response.text.splitlines())
                self._robots[origin] = parser
        except Exception:
            self._robots[origin] = None
        return self._robots[origin]

    async def can_fetch(self, url: str) -> bool:
        parser = await self._robots_for(url)
        if parser is None:
            return True
        return parser.can_fetch(USER_AGENT, url)

    async def fetch_text(self, url: str) -> tuple[str, str]:
        if not await self.can_fetch(url):
            raise PermissionError(f"Blocked by robots.txt: {url}")
        response = await self.fetch(url)
        return response.text, str(response.url)

    async def fetch(self, url: str) -> httpx.Response:
        async with self._semaphore_for(url):
            await asyncio.sleep(self._delay_s + random.uniform(-self._jitter_s, self._jitter_s))
            return await self._fetch_with_retry(url)

    async def _fetch_with_retry(self, url: str, attempt: int = 0) -> httpx.Response:
        try:
            response = await self._client.get(url)
            if response.status_code in (429, 503) and attempt < 4:
                wait = int(response.headers.get("Retry-After", 2**attempt * 5))
                await asyncio.sleep(wait)
                return await self._fetch_with_retry(url, attempt + 1)
            response.raise_for_status()
            return response
        except httpx.TransportError:
            if attempt < 4:
                await asyncio.sleep(2**attempt)
                return await self._fetch_with_retry(url, attempt + 1)
            raise
