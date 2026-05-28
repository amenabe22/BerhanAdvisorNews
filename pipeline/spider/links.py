"""HTML link extraction and URL pattern filtering."""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

from selectolax.parser import HTMLParser

# "/nbe_news/{slug}/" -> regex matching path
_SLUG_PLACEHOLDER = re.compile(r"\{[a-z_]+\}")


def pattern_to_regex(url_pattern: str) -> re.Pattern[str] | None:
    if not url_pattern:
        return None
    path = url_pattern if url_pattern.startswith("/") else urlparse(url_pattern).path
    # Replace {slug} placeholders before re.escape (escape would lock braces literally).
    path_with_slots = _SLUG_PLACEHOLDER.sub("__SLUG__", path)
    regex_body = re.escape(path_with_slots).replace("__SLUG__", r"[^/]+")
    return re.compile(regex_body + r"/?$", re.IGNORECASE)


def is_same_site(url: str, allowed_hosts: set[str]) -> bool:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    return host in allowed_hosts


def extract_links(html: str, base_url: str, allowed_hosts: set[str] | None = None) -> list[str]:
    if allowed_hosts is None:
        base_host = urlparse(base_url).netloc.lower().removeprefix("www.")
        allowed_hosts = {base_host}

    parser = HTMLParser(html)
    found: list[str] = []
    seen: set[str] = set()

    for node in parser.css("a[href]"):
        href = (node.attributes.get("href") or "").strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)
        if parsed.scheme not in ("http", "https"):
            continue
        if not is_same_site(absolute, allowed_hosts):
            continue
        if absolute in seen:
            continue
        seen.add(absolute)
        found.append(absolute)

    return found


def filter_by_patterns(urls: list[str], patterns: list[str]) -> list[str]:
    regexes = [pattern_to_regex(p) for p in patterns if p]
    regexes = [r for r in regexes if r is not None]
    if not regexes:
        return urls

    filtered: list[str] = []
    for url in urls:
        path = urlparse(url).path
        if any(rx.search(path) for rx in regexes):
            filtered.append(url)
    return filtered
