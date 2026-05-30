#!/usr/bin/env python3
"""Run a Phase-3 crawler pass over discovered URLs (no DB writes)."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.crawler.runner import run_crawler_once
from pipeline.db.session import get_session


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run crawler extraction over discovered URLs")
    parser.add_argument("--source", "-s", help="Source code filter, e.g. NBE")
    parser.add_argument("--limit", "-n", type=int, default=10, help="Maximum URLs to process")
    args = parser.parse_args()

    async with get_session() as session:
        rows = await run_crawler_once(
            session,
            limit=max(args.limit, 1),
            source_code=args.source,
        )

    if not rows:
        print("No pending discovered URLs.")
        return

    for row in rows:
        if row.error:
            print(f"[{row.source_code}] extractor=error url={row.url}")
            print(f"  error={row.error}")
            continue
        shadow = "yes" if row.used_shadow else "no"
        print(
            f"[{row.source_code}] extractor={row.extractor} shadow={shadow} "
            f"lang={row.language} url={row.url}"
        )
        print(f"  title={row.title[:120]}")


if __name__ == "__main__":
    asyncio.run(main())
