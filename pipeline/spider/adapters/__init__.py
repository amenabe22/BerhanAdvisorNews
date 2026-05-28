from pipeline.spider.adapters.base import SpiderAdapter
from pipeline.spider.adapters.firma import FIRMAAdapter
from pipeline.spider.adapters.liferay import LiferayAdapter
from pipeline.spider.adapters.listing import ListingAdapter
from pipeline.spider.adapters.rss import RSSAdapter
from pipeline.spider.adapters.sitemap import SitemapAdapter
from pipeline.spider.adapters.wordpress import WordPressAdapter

__all__ = [
    "SpiderAdapter",
    "RSSAdapter",
    "SitemapAdapter",
    "WordPressAdapter",
    "ListingAdapter",
    "LiferayAdapter",
    "FIRMAAdapter",
]
