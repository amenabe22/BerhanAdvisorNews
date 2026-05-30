from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from pipeline.crawler.extractors.registry import run_extractor
from pipeline.crawler.extractors.shadow import extract_shadow
from pipeline.crawler.types import ExtractedContent
from pipeline.utils.language_detector import detect_language


class FetcherLike(Protocol):
    async def fetch_text(self, url: str) -> tuple[str, str]:
        ...


@dataclass
class CrawlRequest:
    source_code: str
    source_url: str
    url: str
    link_metadata: dict[str, Any]


@dataclass
class CrawlOutcome:
    extractor: str
    used_shadow: bool
    content: ExtractedContent


async def crawl_url(request: CrawlRequest, fetcher: FetcherLike) -> CrawlOutcome:
    html, final_url = await fetcher.fetch_text(request.url)
    extractor_name, extracted = run_extractor(
        source_code=request.source_code,
        html=html,
        url=final_url,
        link_metadata=request.link_metadata,
    )

    if _is_empty(extracted):
        extracted = extract_shadow(html=html, url=final_url)
        extracted.language = detect_language(extracted.content)
        return CrawlOutcome(extractor="shadow", used_shadow=True, content=extracted)

    extracted.language = detect_language(extracted.content)
    return CrawlOutcome(
        extractor=extractor_name,
        used_shadow=False,
        content=extracted,
    )


def _is_empty(content: ExtractedContent) -> bool:
    return not (content.content or "").strip()
