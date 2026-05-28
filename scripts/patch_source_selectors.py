#!/usr/bin/env python3
"""Merge selector patches into existing sources (idempotent)."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from pipeline.db.models import Source
from pipeline.db.session import get_session

PATCHES = {
    "NBE": {
        "sitemap_urls": ["https://nbe.gov.et/wp-sitemap.xml"],
    },
    "MOF": {
        "sitemap_url": "https://www.mofed.gov.et/sitemap.xml",
    },
    "MOR": {
        "verify_ssl": False,
    },
    "MOJ": {
        "seed_urls": ["https://justice.gov.et/en/newsroom/"],
    },
}


async def main() -> None:
    async with get_session() as session:
        for code, patch in PATCHES.items():
            result = await session.execute(select(Source).where(Source.code == code))
            source = result.scalar_one_or_none()
            if not source:
                print(f"Skip missing source {code}")
                continue
            merged = dict(source.selectors or {})
            merged.update(patch)
            source.selectors = merged
            print(f"Patched {code}")
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
