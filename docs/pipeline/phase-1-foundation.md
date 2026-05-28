# Phase 1 — Foundation

**Week:** 1  
**Goal:** Postgres schema + Hatchet wired up. Nothing runs yet, but every subsequent phase has a home.

Dependencies: none — this is the base everything else builds on.

---

## Deliverables

- [ ] `git restore .` — restore all tracked files to disk
- [ ] `pipeline/` directory scaffold created
- [ ] All SQLAlchemy models written
- [ ] Alembic migration `001_initial.py` created and tested
- [ ] `docker-compose.yml` at repo root with postgres + Hatchet engine
- [ ] `requirements.txt` updated with full stack
- [ ] `sources` table seeded with NBE, MOF, MOR, MOJ

---

## 1. Directory Layout

```
pipeline/
├── db/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py          # DeclarativeBase
│   │   ├── enums.py         # all PG ENUMs
│   │   ├── sources.py       # sources + source_crawl_state
│   │   ├── schedule.py      # crawl_schedule + crawl_jobs
│   │   ├── urls.py          # discovered_urls
│   │   └── content.py       # content_items + content_versions + extension tables
│   ├── migrations/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 001_initial.py
│   └── session.py           # async engine + get_session
├── spider/
│   └── adapters/            # stubs only in Phase 1
├── crawler/
│   └── extractors/          # stubs only in Phase 1
├── ingestion/
│   └── dedup/               # stubs only in Phase 1
├── workflows/               # stubs only in Phase 1
└── utils/
alembic.ini
docker-compose.yml
requirements.txt
```

---

## 2. Enums (`pipeline/db/models/enums.py`)

```python
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
```

---

## 3. Core Tables

### `sources` — immutable source registry

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| code | VARCHAR UNIQUE | NBE, MOF, MOR, MOJ |
| name | VARCHAR | Human-readable name |
| url | VARCHAR | Base URL |
| source_type | SourceType enum | website / rss / pdf_portal |
| category | SourceCategory enum | government / finance / legal |
| default_language | ContentLanguage enum | |
| selectors | JSONB | CSS selectors, URL patterns |
| crawl_delay_ms | INT | Per-source rate limit |
| max_concurrent_requests | INT | Default 2 |
| request_timeout_ms | INT | Default 60000 |
| is_active | BOOL | Default true |
| created_at | TIMESTAMPTZ | |

### `source_crawl_state` — runtime health (1-to-1 with sources)

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| source_id | UUID FK → sources | |
| last_crawled_at | TIMESTAMPTZ | |
| next_crawl_at | TIMESTAMPTZ | |
| consecutive_errors | INT | Default 0 |
| health_score | INT | Default 100; auto-pause at <= 0 |
| crawl_config | JSONB | Dynamic overrides |
| updated_at | TIMESTAMPTZ | |

### `crawl_schedule` — timing config

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| source_id | UUID FK → sources | |
| cron_expression | VARCHAR | e.g. `*/15 * * * *` |
| priority | INT | Higher = sooner |
| is_paused | BOOL | Default false |
| workflow_type | HatchetWorkflow enum | spider or crawler |
| created_at | TIMESTAMPTZ | |

### `crawl_jobs` — full workflow audit trail

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| source_id | UUID FK → sources | |
| hatchet_run_id | VARCHAR | Hatchet execution ID |
| hatchet_workflow_type | HatchetWorkflow enum | |
| hatchet_step | VARCHAR | Step name |
| worker_id | VARCHAR | |
| status | JobStatus enum | |
| started_at | TIMESTAMPTZ | |
| finished_at | TIMESTAMPTZ | |
| stats | JSONB | urls_found, items_ingested, errors |
| error_message | TEXT | |

### `discovered_urls` — spider↔crawler staging buffer

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| source_id | UUID FK → sources | |
| normalized_url | TEXT | |
| url_hash | VARCHAR(64) UNIQUE | sha256 |
| priority | INT | Default 0 |
| link_metadata | JSONB | anchor text, context |
| discovered_at | TIMESTAMPTZ | |
| crawled_at | TIMESTAMPTZ | NULL until crawler picks it up |
| crawl_job_id | UUID FK → crawl_jobs | |

### `content_items` — unified content store

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| source_id | UUID FK → sources | |
| content_type | ContentType enum | |
| language | ContentLanguage enum | detected |
| canonical_url | TEXT | |
| url_hash | VARCHAR(64) UNIQUE | sha256(canonical_url) |
| content_hash | VARCHAR(64) | sha256(title+body) |
| title | TEXT | |
| raw_content | TEXT | raw HTML stored here |
| extracted_content | TEXT | cleaned markdown/text |
| pipeline_stage | PipelineStage enum | Default: scraped |
| published_at | TIMESTAMPTZ | original publish date |
| scraped_at | TIMESTAMPTZ | ingestion timestamp |
| sibling_document_id | UUID FK → content_items | bilingual pair |
| crawl_job_id | UUID FK → crawl_jobs | |

### `content_versions` — append-only change history

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| content_item_id | UUID FK → content_items | |
| version | INT | monotonic per item |
| content_hash | VARCHAR(64) | snapshot fingerprint |
| title_hash | VARCHAR(64) | |
| body_hash | VARCHAR(64) | |
| attachments_hash | VARCHAR(64) | |
| diff_summary | TEXT | structured change summary |
| raw_html_path | TEXT | GCS path to HTML snapshot |
| created_at | TIMESTAMPTZ | |

---

## 4. Extension Tables (1-to-1 with content_items)

### `articles`

| Column | Type |
|--------|------|
| id | UUID PK |
| content_item_id | UUID FK UNIQUE |
| author | VARCHAR |
| excerpt | TEXT |
| image_url | TEXT |
| word_count | INT |

### `announcements`

| Column | Type |
|--------|------|
| id | UUID PK |
| content_item_id | UUID FK UNIQUE |
| institution_code | VARCHAR |
| announcement_type | VARCHAR |
| reference_number | VARCHAR |

### `releases_docs`

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| content_item_id | UUID FK UNIQUE | |
| directive_type_code | VARCHAR | SBB, FXD, SIB, etc. |
| directive_number | VARCHAR | 04, 62, etc. |
| directive_year | INT | 2026 |
| pdf_url | TEXT | original PDF URL |
| raw_pdf_path | TEXT | GCS path |
| ocr_text | TEXT | Tesseract output if scanned |
| amends_directive_id | UUID FK → releases_docs | self-referencing |
| repealed_by_id | UUID FK → releases_docs | self-referencing |

---

## 5. Pre-seeded Sources

Seed data for `sources` table, verified May 2026:

| code | name | url | source_type | category | default_language | crawl_delay_ms |
|------|------|-----|------------|----------|-----------------|---------------|
| NBE | National Bank of Ethiopia | https://nbe.gov.et | website | finance | en | 2000 |
| MOF | Ministry of Finance | https://www.mofed.gov.et | website | finance | en | 1500 |
| MOR | Ministry of Revenue | https://www.mor.gov.et | website | government | en | 3000 |
| MOJ | Ministry of Justice | https://justice.gov.et | website | legal | en | 4000 |

NBE selectors config (store in `sources.selectors` JSONB):

```json
{
  "news_listing": "/news/press-release/",
  "archive_listing": "/all-news/",
  "article_url_pattern": "/nbe_news/{slug}/",
  "directives_listing": "/mandates/directives/",
  "directive_url_pattern": "/files/{slug}/",
  "directive_regex": "^/files/([a-z-]+)-(\\d+)-(\\d{4})/",
  "title_selector": "h1.entry-title",
  "date_selector": "time.entry-date",
  "body_selector": ".elementor-widget-text-editor",
  "amharic_prefix": "/am/"
}
```

---

## 6. docker-compose.yml (root)

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: berhan_pipeline
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data

  hatchet-engine:
    image: ghcr.io/hatchet-dev/hatchet/hatchet-engine:latest
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/berhan_pipeline
      SERVER_AUTH_COOKIE_SECRETS: "secret1 secret2"
    ports:
      - "7070:7070"

  hatchet-dashboard:
    image: ghcr.io/hatchet-dev/hatchet/hatchet-dashboard:latest
    depends_on:
      - hatchet-engine
    ports:
      - "8080:80"

volumes:
  pg_data:
```

---

## 7. requirements.txt (root)

```
# Core
sqlalchemy[asyncio]==2.x
asyncpg
alembic
pydantic>=2
python-dotenv

# Workflow
hatchet-sdk

# HTTP + parsing
httpx[http2]
selectolax
beautifulsoup4
lxml
feedparser
playwright

# Content extraction
trafilatura
readability-lxml

# PDF
pdfplumber
pytesseract
Pillow

# Language detection
lingua-language-detector

# Utils
hashlib  # stdlib
loguru
```

---

## Completion Checklist

- [ ] `pipeline/db/models/` — all 7 model files written and importable
- [ ] `alembic upgrade head` runs without errors
- [ ] All 4 sources inserted via seed script
- [ ] `docker-compose up` starts postgres + hatchet without errors
- [ ] Hatchet dashboard accessible at http://localhost:8080
