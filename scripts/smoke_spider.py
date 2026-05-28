#!/usr/bin/env python3
"""Smoke test: each source adapter discovers >= 1 URL (no DB required)."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from pipeline.db.models import Source
from pipeline.db.session import get_session_factory
from pipeline.spider.http import SpiderHttp
from pipeline.spider.registry import build_adapters


async def smoke() -> int:
    factory = get_session_factory()
    failures: list[str] = []

    async with factory() as session:
        result = await session.execute(
            select(Source).where(Source.is_active.is_(True)).order_by(Source.code)
        )
        sources = list(result.scalars().all())

    for source in sources:
        http = SpiderHttp(
            crawl_delay_ms=min(source.crawl_delay_ms, 500),
            max_concurrent=source.max_concurrent_requests,
        )
        try:
            adapters = build_adapters(source, http)
            total = 0
            print(f"\n=== {source.code} ({source.url}) ===")
            for adapter in adapters:
                name = adapter.__class__.__name__
                try:
                    urls = await adapter.discover_urls(source)
                    total += len(urls)
                    sample = urls[0] if urls else "-"
                    print(f"  {name}: {len(urls)} urls  sample={sample[:80]}")
                except Exception as exc:
                    print(f"  {name}: ERROR {exc}")
                    failures.append(f"{source.code}/{name}: {exc}")

            if total == 0:
                failures.append(f"{source.code}: no URLs discovered")
                print("  FAIL: zero URLs")
            else:
                print(f"  OK: {total} total URLs")
        finally:
            await http.aclose()

    if failures:
        print("\nFailures:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("\nAll sources passed smoke test.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(smoke()))
