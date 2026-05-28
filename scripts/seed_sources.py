#!/usr/bin/env python3
"""Seed government sources, crawl state, and spider schedules."""

import asyncio
import sys
from pathlib import Path

# Repo root on PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from pipeline.db.models import (
    ContentLanguage,
    CrawlSchedule,
    HatchetWorkflow,
    Source,
    SourceCategory,
    SourceCrawlState,
    SourceType,
)
from pipeline.db.session import get_session

SOURCES = [
    {
        "code": "NBE",
        "name": "National Bank of Ethiopia",
        "url": "https://nbe.gov.et",
        "source_type": SourceType.website,
        "category": SourceCategory.finance,
        "default_language": ContentLanguage.en,
        "crawl_delay_ms": 2000,
        "cron": "*/20 * * * *",
        "selectors": {
            "cms": "wordpress_elementor",
            "news_listing": "/news/press-release/",
            "archive_listing": "/all-news/",
            "article_url_pattern": "/nbe_news/{slug}/",
            "directives_listing": "/mandates/directives/",
            "directive_url_pattern": "/files/{slug}/",
            "directive_regex": "^/files/([a-z-]+)-(\\d+)-(\\d{4})/",
            "title_selector": "h1.entry-title",
            "date_selector": "time.entry-date",
            "body_selector": ".elementor-widget-text-editor",
            "amharic_prefix": "/am/",
            "sitemap_url": "https://nbe.gov.et/sitemap.xml",
            "sitemap_urls": [
                "https://nbe.gov.et/wp-sitemap.xml",
            ],
            "canary_urls": [
                "https://nbe.gov.et/nbe_news/authorization-for-commercial-banks-to-issue-export-permits-for-exports-to-the-peoples-republic-of-china/",
                "https://nbe.gov.et/files/fxd-04-2026/",
                "https://nbe.gov.et/news/press-release/",
            ],
        },
    },
    {
        "code": "MOF",
        "name": "Ministry of Finance",
        "url": "https://www.mofed.gov.et",
        "source_type": SourceType.website,
        "category": SourceCategory.finance,
        "default_language": ContentLanguage.en,
        "crawl_delay_ms": 1500,
        "cron": "*/15 * * * *",
        "selectors": {
            "cms": "django_mezzanine",
            "news_listing": "/press-media/news/",
            "article_url_pattern": "/blog/{slug}/",
            "directives_base": "/mof-directive/",
            "title_selector": "h1",
            "body_selector": "div.blog-detail p, article p",
            "pdf_path_pattern": "/media/filer_public/",
            "sitemap_url": "https://www.mofed.gov.et/sitemap.xml",
            "canary_urls": [
                "https://www.mofed.gov.et/blog/imf-reaffirms-strong-support-for-ethiopias-reform-agenda-amid-global-pressures/",
                "https://www.mofed.gov.et/press-media/news/",
            ],
        },
    },
    {
        "code": "MOR",
        "name": "Ministry of Revenue",
        "url": "https://www.mor.gov.et",
        "source_type": SourceType.website,
        "category": SourceCategory.government,
        "default_language": ContentLanguage.en,
        "crawl_delay_ms": 3000,
        "cron": "0 * * * *",
        "selectors": {
            "cms": "liferay",
            "alternate_base_url": "https://mor.gov.et",
            "respect_robots_txt": True,
            "verify_ssl": False,
            "requires_playwright_fallback": True,
            "canary_urls": [
                "https://www.mor.gov.et/",
            ],
        },
    },
    {
        "code": "MOJ",
        "name": "Ministry of Justice",
        "url": "https://justice.gov.et",
        "source_type": SourceType.website,
        "category": SourceCategory.legal,
        "default_language": ContentLanguage.en,
        "crawl_delay_ms": 4000,
        "cron": "0 */2 * * *",
        "selectors": {
            "cms": "firma",
            "news_listing": "/en/newsroom/",
            "title_selector": "h1",
            "body_selector": ".newsroom-body, article .content",
            "max_retries": 5,
            "seed_urls": [
                "https://justice.gov.et/en/newsroom/",
            ],
            "canary_urls": [
                "https://justice.gov.et/en/newsroom/",
            ],
        },
    },
]


async def seed() -> None:
    async with get_session() as session:
        for spec in SOURCES:
            existing = await session.execute(
                select(Source).where(Source.code == spec["code"])
            )
            if existing.scalar_one_or_none():
                print(f"Skip existing source: {spec['code']}")
                continue

            source = Source(
                code=spec["code"],
                name=spec["name"],
                url=spec["url"],
                source_type=spec["source_type"],
                category=spec["category"],
                default_language=spec["default_language"],
                selectors=spec["selectors"],
                crawl_delay_ms=spec["crawl_delay_ms"],
                max_concurrent_requests=2,
                request_timeout_ms=60000,
                is_active=True,
            )
            session.add(source)
            await session.flush()

            session.add(
                SourceCrawlState(
                    source_id=source.id,
                    health_score=100,
                    consecutive_errors=0,
                )
            )
            session.add(
                CrawlSchedule(
                    source_id=source.id,
                    cron_expression=spec["cron"],
                    priority=10,
                    is_paused=False,
                    workflow_type=HatchetWorkflow.spider,
                )
            )
            print(f"Seeded source: {spec['code']} ({source.id})")

    print("Done.")


def main() -> None:
    asyncio.run(seed())


if __name__ == "__main__":
    main()
