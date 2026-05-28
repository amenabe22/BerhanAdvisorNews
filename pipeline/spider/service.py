from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pipeline.db.models.sources import Source
from pipeline.spider.http import SpiderHttp
from pipeline.spider.registry import build_adapters
from pipeline.spider.repository import InsertStats, insert_discovered_urls


@dataclass
class SpiderRunResult:
    source_code: str
    urls_found: int
    inserted: int
    skipped: int
    adapter_counts: dict[str, int]


async def run_spider_for_source(
    session: AsyncSession,
    source: Source,
) -> SpiderRunResult:
    selectors = source.selectors or {}
    http = SpiderHttp(
        crawl_delay_ms=source.crawl_delay_ms,
        max_concurrent=source.max_concurrent_requests,
        timeout_s=source.request_timeout_ms / 1000.0,
        verify_ssl=bool(selectors.get("verify_ssl", True)),
    )
    try:
        adapters = build_adapters(source, http)
        all_urls: list[str] = []
        adapter_counts: dict[str, int] = {}

        for adapter in adapters:
            name = adapter.__class__.__name__
            urls = await adapter.discover_urls(source)
            adapter_counts[name] = len(urls)
            all_urls.extend(urls)

        # Deduplicate raw URLs before insert
        unique_urls = list(dict.fromkeys(all_urls))
        stats: InsertStats = await insert_discovered_urls(
            session, source.id, unique_urls
        )

        return SpiderRunResult(
            source_code=source.code,
            urls_found=len(unique_urls),
            inserted=stats.inserted,
            skipped=stats.skipped,
            adapter_counts=adapter_counts,
        )
    finally:
        await http.aclose()


async def run_spider_by_code(session: AsyncSession, source_code: str) -> SpiderRunResult:
    result = await session.execute(select(Source).where(Source.code == source_code))
    source = result.scalar_one_or_none()
    if source is None:
        raise ValueError(f"Unknown source code: {source_code}")
    if not source.is_active:
        raise ValueError(f"Source {source_code} is not active")
    return await run_spider_for_source(session, source)


async def run_spider_all(session: AsyncSession) -> list[SpiderRunResult]:
    result = await session.execute(select(Source).where(Source.is_active.is_(True)))
    sources = list(result.scalars().all())
    results: list[SpiderRunResult] = []
    for source in sources:
        results.append(await run_spider_for_source(session, source))
    return results
