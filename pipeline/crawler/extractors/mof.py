from __future__ import annotations

from selectolax.parser import HTMLParser

from pipeline.crawler.extractors.common import (
    canonical_url,
    collect_attachments,
    first_text,
    text_content,
)
from pipeline.crawler.types import ExtractedContent


def extract_mof(html: str, url: str) -> ExtractedContent:
    parser = HTMLParser(html)
    title = first_text(parser, ["h1", "title"])
    body = text_content(parser, ["div.blog-detail p", "article p", "main p", "p"])
    attachments = collect_attachments(
        parser, url, "/media/filer_public/", ".pdf", "pdf"
    )

    return ExtractedContent(
        title=title,
        content=body,
        attachments=attachments,
        raw_html=html,
        canonical_url=canonical_url(parser, url),
    )
