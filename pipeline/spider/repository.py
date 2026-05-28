from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from pipeline.db.models.urls import DiscoveredUrl
from pipeline.utils.directive_meta import extract_directive_meta
from pipeline.utils.url_normalizer import normalize_url, url_hash


@dataclass
class InsertStats:
    discovered: int
    inserted: int
    skipped: int


def build_link_metadata(raw_url: str) -> dict:
    meta: dict = {"raw_url": raw_url}
    directive = extract_directive_meta(urlparse(raw_url).path)
    if directive:
        meta.update(directive)
    return meta


async def insert_discovered_urls(
    session: AsyncSession,
    source_id: uuid.UUID,
    raw_urls: list[str],
    *,
    priority: int = 0,
) -> InsertStats:
    seen_hashes: set[str] = set()
    inserted = 0
    skipped = 0
    now = datetime.now(timezone.utc)

    for raw_url in raw_urls:
        if not raw_url or not raw_url.startswith("http"):
            skipped += 1
            continue

        normalized = normalize_url(raw_url)
        if not normalized:
            skipped += 1
            continue

        hash_value = url_hash(normalized)
        if hash_value in seen_hashes:
            skipped += 1
            continue
        seen_hashes.add(hash_value)

        stmt = (
            pg_insert(DiscoveredUrl)
            .values(
                source_id=source_id,
                normalized_url=normalized,
                url_hash=hash_value,
                priority=priority,
                link_metadata=build_link_metadata(raw_url),
                discovered_at=now,
            )
            .on_conflict_do_nothing(index_elements=["url_hash"])
            .returning(DiscoveredUrl.id)
        )
        result = await session.execute(stmt)
        if result.fetchone():
            inserted += 1
        else:
            skipped += 1

    return InsertStats(discovered=len(raw_urls), inserted=inserted, skipped=skipped)
