"""Shared HTTP client for spider discovery (rate-limited, polite)."""

from __future__ import annotations

import asyncio
import random
from typing import Any
from urllib.parse import urlparse

import httpx

USER_AGENT = "BerhanAdvisorBot/1.0 (+https://berhanadvisor.com/bot)"


class SpiderHttp:
    def __init__(
        self,
        crawl_delay_ms: int = 2000,
        max_concurrent: int = 2,
        timeout_s: float = 60.0,
        verify_ssl: bool = True,
    ) -> None:
        self._delay_s = crawl_delay_ms / 1000.0
        self._semaphores: dict[str, asyncio.Semaphore] = {}
        self._max_concurrent = max_concurrent
        self._client = httpx.AsyncClient(
            headers={"User-Agent": USER_AGENT},
            timeout=httpx.Timeout(15.0, read=timeout_s),
            follow_redirects=True,
            verify=verify_ssl,
        )

    def _semaphore_for(self, url: str) -> asyncio.Semaphore:
        host = urlparse(url).netloc or "default"
        if host not in self._semaphores:
            self._semaphores[host] = asyncio.Semaphore(self._max_concurrent)
        return self._semaphores[host]

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        async with self._semaphore_for(url):
            await asyncio.sleep(self._delay_s + random.uniform(-0.2, 0.2))
            return await self._get_with_retry(url, **kwargs)

    async def _get_with_retry(self, url: str, attempt: int = 0, **kwargs: Any) -> httpx.Response:
        try:
            response = await self._client.get(url, **kwargs)
            if response.status_code in (429, 503) and attempt < 4:
                retry_after = int(response.headers.get("Retry-After", 2**attempt * 5))
                await asyncio.sleep(retry_after)
                return await self._get_with_retry(url, attempt + 1, **kwargs)
            response.raise_for_status()
            return response
        except httpx.TransportError:
            if attempt < 4:
                await asyncio.sleep(2**attempt)
                return await self._get_with_retry(url, attempt + 1, **kwargs)
            raise

    async def aclose(self) -> None:
        await self._client.aclose()
