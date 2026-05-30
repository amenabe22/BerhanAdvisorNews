from __future__ import annotations

from selectolax.parser import HTMLParser

from pipeline.crawler.extractors.common import first_iso_date_in_text
from pipeline.crawler.types import ExtractedContent

SHADOW_REVIEW_QUEUE = "shadow_review"


def extract_shadow(html: str, url: str) -> ExtractedContent:
    parser = HTMLParser(html)

    title = ""
    title_node = parser.css_first("title")
    if title_node:
        title = (title_node.text() or "").strip().split(" - ")[0].strip()

    best = ""
    for node in parser.css("main,article,section,div,p"):
        text = (node.text() or "").strip()
        if len(text) > len(best):
            best = text

    published_at = first_iso_date_in_text(html)
    return ExtractedContent(
        title=title or "Untitled",
        content=best.strip(),
        published_at=published_at,
        raw_html=html,
        canonical_url=url,
    )
