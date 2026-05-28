import enum


class ContentLanguage(str, enum.Enum):
    am = "am"
    en = "en"
    om = "om"
    ti = "ti"
    so = "so"
    mixed = "mixed"


class SourceType(str, enum.Enum):
    website = "website"
    rss = "rss"
    api = "api"
    pdf_portal = "pdf_portal"
    social = "social"


class SourceCategory(str, enum.Enum):
    legal = "legal"
    finance = "finance"
    politics = "politics"
    business = "business"
    general_news = "general_news"
    government = "government"
    regional = "regional"
    international = "international"


class ContentType(str, enum.Enum):
    article = "article"
    release = "release"
    announcement = "announcement"
    proclamation = "proclamation"
    document = "document"
    press_release = "press_release"


class HatchetWorkflow(str, enum.Enum):
    spider = "spider"
    crawler = "crawler"


class JobStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    skipped = "skipped"
    retrying = "retrying"


class PipelineStage(str, enum.Enum):
    scraped = "scraped"
    processed = "processed"
    ingested = "ingested"
    published = "published"
