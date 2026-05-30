from __future__ import annotations

from typing import Any, Callable

from pipeline.crawler.extractors.firma import extract_firma
from pipeline.crawler.extractors.liferay import extract_liferay
from pipeline.crawler.extractors.mof import extract_mof
from pipeline.crawler.extractors.nbe import extract_nbe
from pipeline.crawler.extractors.readability import extract_readability
from pipeline.crawler.types import ExtractedContent

ExtractorFn = Callable[..., ExtractedContent]


def select_extractor(source_code: str) -> tuple[str, ExtractorFn]:
    code = (source_code or "").upper()
    if code == "NBE":
        return "nbe", extract_nbe
    if code == "MOF":
        return "mof", extract_mof
    if code == "MOR":
        return "liferay", extract_liferay
    if code == "MOJ":
        return "firma", extract_firma
    return "readability", extract_readability


def run_extractor(
    source_code: str,
    html: str,
    url: str,
    link_metadata: dict[str, Any] | None = None,
) -> tuple[str, ExtractedContent]:
    name, fn = select_extractor(source_code)
    if name == "nbe":
        return name, fn(html=html, url=url, link_metadata=link_metadata or {})
    return name, fn(html=html, url=url)
