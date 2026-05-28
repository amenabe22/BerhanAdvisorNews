"""robots.txt enforcement for spider discovery."""

from __future__ import annotations

from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

from pipeline.spider.http import SpiderHttp, USER_AGENT


class RobotsChecker:
    def __init__(self, base_url: str, http: SpiderHttp) -> None:
        self._base_url = base_url.rstrip("/")
        self._http = http
        self._parsers: dict[str, RobotFileParser | None] = {}

    async def _parser_for(self, url: str) -> RobotFileParser | None:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin in self._parsers:
            return self._parsers[origin]

        robots_url = urljoin(origin + "/", "robots.txt")
        parser = RobotFileParser()
        try:
            response = await self._http.get(robots_url)
            parser.parse(response.text.splitlines())
            self._parsers[origin] = parser
        except Exception:
            self._parsers[origin] = None
        return self._parsers[origin]

    async def can_fetch(self, url: str) -> bool:
        parser = await self._parser_for(url)
        if parser is None:
            return True
        return parser.can_fetch(USER_AGENT, url)
