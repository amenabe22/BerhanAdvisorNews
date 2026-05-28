#!/usr/bin/env python3
"""Run URL discovery spider for one or all sources."""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.db.session import get_session
from pipeline.spider.service import run_spider_all, run_spider_by_code


async def main() -> None:
    parser = argparse.ArgumentParser(description="Discover URLs for government sources")
    parser.add_argument(
        "--source",
        "-s",
        help="Source code (NBE, MOF, MOR, MOJ). Omit to run all active sources.",
    )
    args = parser.parse_args()

    async with get_session() as session:
        if args.source:
            results = [await run_spider_by_code(session, args.source.upper())]
        else:
            results = await run_spider_all(session)

    for r in results:
        print(f"\n[{r.source_code}] found={r.urls_found} inserted={r.inserted} skipped={r.skipped}")
        for adapter, count in r.adapter_counts.items():
            print(f"  {adapter}: {count} urls")


if __name__ == "__main__":
    asyncio.run(main())
