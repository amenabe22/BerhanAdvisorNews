from __future__ import annotations

from readability import Document
from selectolax.parser import HTMLParser
import trafilatura

from pipeline.crawler.extractors.common import canonical_url, first_text, text_content
from pipeline.crawler.types import ExtractedContent


def extract_readability(html: str, url: str) -> ExtractedContent:
    extracted = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=False,
        output_format="markdown",
    )
    if extracted:
        title = Document(html).short_title() or ""
        return ExtractedContent(
            title=title.strip(),
            content=extracted.strip(),
            raw_html=html,
            canonical_url=url,
        )

    # Secondary fallback through readability-lxml
    doc = Document(html)
    summary_html = doc.summary()
    title = (doc.short_title() or "").strip()
    summary_text = text_content(HTMLParser(summary_html), ["p", "div"])
    parser = HTMLParser(html)
    return ExtractedContent(
        title=title or first_text(parser, ["title"]),
        content=summary_text.strip(),
        raw_html=html,
        canonical_url=canonical_url(parser, url),
    )
