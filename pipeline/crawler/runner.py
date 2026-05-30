from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pipeline.crawler.fetcher.http import HTTPFetcher
from pipeline.crawler.service import CrawlRequest, crawl_url
from pipeline.db.models import DiscoveredUrl, Source


@dataclass
class CrawlRunItem:
    source_code: str
    url: str
    extractor: str
    used_shadow: bool
    language: str
    title: str
    error: str | None = None


async def run_crawler_once(
    session: AsyncSession,
    *,
    limit: int = 10,
    source_code: str | None = None,
) -> list[CrawlRunItem]:
    stmt = (
        select(DiscoveredUrl, Source)
        .join(Source, DiscoveredUrl.source_id == Source.id)
        .where(DiscoveredUrl.crawled_at.is_(None), Source.is_active.is_(True))
        .order_by(DiscoveredUrl.discovered_at.asc())
        .limit(limit)
    )
    if source_code:
        stmt = stmt.where(Source.code == source_code.upper())

    rows = list((await session.execute(stmt)).all())
    if not rows:
        return []

    fetcher = HTTPFetcher()
    try:
        out: list[CrawlRunItem] = []
        for discovered, source in rows:
            fetch_url = (discovered.link_metadata or {}).get("raw_url") or discovered.normalized_url
            req = CrawlRequest(
                source_code=source.code,
                source_url=source.url,
                url=fetch_url,
                link_metadata=discovered.link_metadata or {},
            )
            try:
                result = await crawl_url(req, fetcher)
                out.append(
                    CrawlRunItem(
                        source_code=source.code,
                        url=fetch_url,
                        extractor=result.extractor,
                        used_shadow=result.used_shadow,
                        language=result.content.language,
                        title=result.content.title,
                    )
                )
            except Exception as exc:
                out.append(
                    CrawlRunItem(
                        source_code=source.code,
                        url=fetch_url,
                        extractor="error",
                        used_shadow=False,
                        language="",
                        title="",
                        error=f"{exc.__class__.__name__}: {exc}",
                    )
                )
        return out
    finally:
        await fetcher.close()
