"""Source-specific extractors (Phase 3)."""

from pipeline.crawler.extractors.firma import extract_firma
from pipeline.crawler.extractors.liferay import extract_liferay
from pipeline.crawler.extractors.mof import extract_mof
from pipeline.crawler.extractors.nbe import extract_nbe
from pipeline.crawler.extractors.readability import extract_readability
from pipeline.crawler.extractors.shadow import SHADOW_REVIEW_QUEUE, extract_shadow

__all__ = [
    "extract_nbe",
    "extract_mof",
    "extract_liferay",
    "extract_firma",
    "extract_readability",
    "extract_shadow",
    "SHADOW_REVIEW_QUEUE",
]
