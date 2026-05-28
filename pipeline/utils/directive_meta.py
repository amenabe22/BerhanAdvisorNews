"""Extract NBE directive metadata from URL paths before HTTP fetch."""

import re
from typing import Any

# /files/fxd-04-2026/, /files/nbe-int-13-2026/
DIRECTIVE_REGEX = re.compile(
    r"/files/([a-z](?:[a-z-]*[a-z])?)-(\d+)-(\d{4})/?$",
    re.IGNORECASE,
)


def extract_directive_meta(path: str) -> dict[str, Any] | None:
    match = DIRECTIVE_REGEX.search(path)
    if not match:
        return None
    type_code = match.group(1).upper().replace("-", "_")
    return {
        "directive_type_code": type_code,
        "directive_number": match.group(2),
        "directive_year": int(match.group(3)),
    }
