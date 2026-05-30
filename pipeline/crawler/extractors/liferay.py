from __future__ import annotations

from urllib.parse import urljoin

from selectolax.parser import HTMLParser

from pipeline.crawler.extractors.common import canonical_url, first_text, text_content
from pipeline.crawler.types import ExtractedContent


def extract_liferay(html: str, url: str) -> ExtractedContent:
    parser = HTMLParser(html)
    title = first_text(parser, ["h1", ".portlet-title-text", "title"])
    body = text_content(parser, [".journal-content-article p", "article p", "main p", "p"])

    attachments: list[dict[str, str]] = []
    seen: set[str] = set()
    for node in parser.css("a[href*='/documents/'],a[href*='/download/']"):
        href = (node.attributes.get("href") or "").strip()
        if not href:
            continue
        abs_url = urljoin(url, href)
        if abs_url in seen:
            continue
        seen.add(abs_url)
        kind = "pdf" if abs_url.lower().endswith(".pdf") else "document"
        attachments.append({"url": abs_url, "type": kind})

    return ExtractedContent(
        title=title,
        content=body,
        attachments=attachments,
        raw_html=html,
        canonical_url=canonical_url(parser, url),
    )
