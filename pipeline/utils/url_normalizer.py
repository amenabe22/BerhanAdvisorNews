"""URL normalization and hashing for deduplication."""

import hashlib
import re
from urllib.parse import parse_qsl, unquote, urlencode, urlparse, urlunparse

STRIP_PARAMS = frozenset(
    {
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_content",
        "utm_term",
        "fbclid",
        "gclid",
        "ref",
        "source",
        "mc_cid",
        "mc_eid",
    }
)

# Ethiopic script range for optional path decoding
_ETHIOPIC = re.compile(r"[\u1200-\u137f]")


def normalize_url(raw_url: str) -> str:
    """Canonical form for deduplication and storage."""
    raw_url = raw_url.strip()
    if not raw_url:
        return raw_url

    parsed = urlparse(raw_url)
    scheme = (parsed.scheme or "https").lower()
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]

    path = parsed.path.rstrip("/") or ""
    # Decode percent-encoded paths (e.g. Amharic slugs on MOF)
    if "%" in path:
        decoded = unquote(path)
        if _ETHIOPIC.search(decoded):
            path = decoded

    params = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True) if k not in STRIP_PARAMS]
    query = urlencode(params) if params else ""

    return urlunparse((scheme, host, path, "", query, ""))


def url_hash(normalized_url: str) -> str:
    return hashlib.sha256(normalized_url.encode("utf-8")).hexdigest()
