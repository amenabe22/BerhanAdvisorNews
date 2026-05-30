from __future__ import annotations

from typing import Any

from selectolax.parser import HTMLParser

from pipeline.crawler.extractors.common import (
    canonical_url,
    collect_attachments,
    first_text,
    parse_iso_datetime,
    text_content,
)
from pipeline.crawler.types import ExtractedContent


def extract_nbe(html: str, url: str, link_metadata: dict[str, Any] | None = None) -> ExtractedContent:
    parser = HTMLParser(html)
    title = first_text(parser, ["h1.entry-title", "h1", "title"])

    published_at = None
    time_node = parser.css_first("time.entry-date")
    if time_node:
        published_at = parse_iso_datetime(time_node.attributes.get("datetime"))

    body = text_content(parser, [".elementor-widget-text-editor p", "article p", "main p", "p"])
    attachments = collect_attachments(
        parser, url, "/wp-content/uploads/", ".pdf", "pdf"
    )

    meta = link_metadata or {}
    return ExtractedContent(
        title=title,
        content=body,
        published_at=published_at,
        attachments=attachments,
        directive_number=meta.get("directive_number"),
        directive_type_code=meta.get("directive_type_code"),
        raw_html=html,
        canonical_url=canonical_url(parser, url),
    )
