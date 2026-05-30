from __future__ import annotations

from selectolax.parser import HTMLParser

from pipeline.crawler.extractors.common import (
    canonical_url,
    first_text,
    parse_iso_datetime,
    text_content,
)
from pipeline.crawler.types import ExtractedContent


def extract_firma(html: str, url: str) -> ExtractedContent:
    parser = HTMLParser(html)
    title = first_text(parser, ["h1", ".newsroom-title", "title"])
    body = text_content(parser, [".newsroom-body p", "article .content p", "article p", "p"])

    published_at = None
    time_node = parser.css_first(".news-date, time")
    if time_node:
        published_at = parse_iso_datetime(
            time_node.attributes.get("datetime") or (time_node.text() or "").strip()
        )

    return ExtractedContent(
        title=title,
        content=body,
        published_at=published_at,
        raw_html=html,
        canonical_url=canonical_url(parser, url),
    )
