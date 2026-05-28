from __future__ import annotations

from pipeline.db.models.sources import Source
from pipeline.spider.adapters.base import SpiderAdapter
from pipeline.spider.adapters.firma import FIRMAAdapter
from pipeline.spider.adapters.liferay import LiferayAdapter
from pipeline.spider.adapters.listing import ListingAdapter
from pipeline.spider.adapters.rss import RSSAdapter
from pipeline.spider.adapters.sitemap import SitemapAdapter
from pipeline.spider.adapters.wordpress import WordPressAdapter
from pipeline.spider.http import SpiderHttp
from pipeline.spider.robots import RobotsChecker

CMS_PRIMARY = {
    "wordpress_elementor": WordPressAdapter,
    "django_mezzanine": ListingAdapter,
    "liferay": LiferayAdapter,
    "firma": FIRMAAdapter,
}


def build_adapters(source: Source, http: SpiderHttp) -> list[SpiderAdapter]:
    """Primary CMS adapter + sitemap + optional RSS."""
    selectors = source.selectors or {}
    robots = RobotsChecker(source.url, http)
    adapters: list[SpiderAdapter] = []

    cms = selectors.get("cms")
    primary_cls = CMS_PRIMARY.get(cms or "")
    if primary_cls:
        adapters.append(primary_cls(http, robots))

    adapters.append(SitemapAdapter(http, robots))

    if selectors.get("rss_url") or selectors.get("use_rss", False):
        adapters.append(RSSAdapter(http, robots))

    return adapters
