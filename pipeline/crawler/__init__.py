"""Page fetch and content extraction (Phase 3)."""

from pipeline.crawler.service import CrawlOutcome, CrawlRequest, crawl_url
from pipeline.crawler.types import ExtractedContent

__all__ = ["ExtractedContent", "CrawlRequest", "CrawlOutcome", "crawl_url"]
