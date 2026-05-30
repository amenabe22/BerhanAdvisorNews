from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urljoin

from selectolax.parser import HTMLParser


def parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    raw = value.strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def text_content(parser: HTMLParser, selectors: list[str]) -> str:
    parts: list[str] = []
    for selector in selectors:
        for node in parser.css(selector):
            text = (node.text() or "").strip()
            if text:
                parts.append(text)
        if parts:
            break
    return "\n\n".join(parts).strip()


def first_text(parser: HTMLParser, selectors: list[str]) -> str:
    for selector in selectors:
        node = parser.css_first(selector)
        if node:
            text = (node.text() or "").strip()
            if text:
                return text
    return ""


def canonical_url(parser: HTMLParser, fallback_url: str) -> str:
    for selector, attr in [
        ("meta[property='og:url']", "content"),
        ("link[rel='canonical']", "href"),
    ]:
        node = parser.css_first(selector)
        if not node:
            continue
        value = (node.attributes.get(attr) or "").strip()
        if value:
            return value
    return fallback_url


def collect_attachments(
    parser: HTMLParser,
    base_url: str,
    href_contains: str,
    suffix: str,
    attachment_type: str,
) -> list[dict[str, str]]:
    selector = f"a[href*='{href_contains}'][href$='{suffix}']"
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for node in parser.css(selector):
        href = (node.attributes.get("href") or "").strip()
        if not href:
            continue
        abs_url = urljoin(base_url, href)
        if abs_url in seen:
            continue
        seen.add(abs_url)
        out.append({"url": abs_url, "type": attachment_type})
    return out


_ISO_DATE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


def first_iso_date_in_text(text: str) -> datetime | None:
    match = _ISO_DATE.search(text or "")
    if not match:
        return None
    return parse_iso_datetime(match.group(1))
