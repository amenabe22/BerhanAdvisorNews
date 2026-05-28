# Phase 8 — Monitoring & Replay

**Week:** 5+  
**Goal:** Ensure every crawl job is observable, every failure is replayable, and the pipeline can be re-run against stored raw data without fetching the internet again.  
**Depends on:** Phases 1–7

---

## Deliverables

- [ ] Raw HTML stored to GCS on every successful page fetch
- [ ] Raw PDF stored to GCS (handled in Phase 4, verified here)
- [ ] Replay CLI: re-run extraction from stored raw HTML
- [ ] Replay CLI: re-run ingestion from stored extracted content
- [ ] Cross-source reconciliation job (daily)
- [ ] `crawl_jobs` query tools for operational visibility

---

## Why Raw Storage Is Non-Negotiable

From the build guide:

> "The most valuable thing you can build early is a stable, replayable, debuggable ingestion pipeline. Because extraction logic changes, AI improves, parsers improve, OCR improves. But if you lose raw HTML, raw PDFs, crawl history, version history — you can never reconstruct the timeline later."

The raw store is the reprocessing layer. It allows:
- Rerunning a better extractor version against old crawls
- Recovering from a bug that corrupted `content_items`
- Auditing what was on a page on a specific date
- Training ML models on real crawl data

---

## 1. Raw HTML Storage

Every page fetch in `fetch_page` (Phase 6 Step 1) stores the raw HTML to GCS **before** extraction.

```python
GCS_HTML_PREFIX = "raw_html"

async def store_raw_html(html: str, source_code: str, url_hash: str, crawl_job_id: str) -> str:
    """Returns GCS path."""
    date_path = datetime.utcnow().strftime("%Y/%m/%d")
    gcs_path = f"{GCS_HTML_PREFIX}/{source_code}/{date_path}/{url_hash[:8]}.html.gz"

    bucket = gcs.Client().bucket(GCS_BUCKET)
    blob = bucket.blob(gcs_path)
    blob.upload_from_string(
        gzip.compress(html.encode()),
        content_type="text/html",
    )
    return gcs_path
```

Store the `gcs_path` in `content_items.raw_content` (repurposed as a GCS path reference).

**Retention:** indefinite. Never delete raw HTML.

---

## 2. Replay Tooling (`pipeline/utils/replay.py`)

### Replay by `crawl_jobs.id`

Re-runs extraction from stored raw HTML. No HTTP fetch — reads from GCS.

```bash
python -m pipeline.tools.replay --job-id <uuid>
```

```python
async def replay_job(job_id: UUID):
    async with get_session() as session:
        job = await session.get(CrawlJob, job_id)
        # Get the discovered URL + source from the job
        # Fetch raw HTML from GCS (stored in content_items.raw_content)
        # Re-run: extract_content → detect_language → handle_pdf → ingest
        # Write new content_items / content_versions row
```

### Replay extraction only (new extractor version)

Useful when a better extractor is deployed and old content needs to be reprocessed:

```bash
python -m pipeline.tools.replay-extraction \
  --source-code NBE \
  --since 2026-01-01 \
  --extractor nbe
```

This reads stored raw HTML from GCS for all NBE items scraped since the given date, runs the updated extractor, and writes a new `content_versions` row if the output differs.

### Replay ingestion only

Useful after schema migrations or deduplication fixes:

```bash
python -m pipeline.tools.replay-ingestion --source-code MOF
```

Re-runs Phase 5 logic against already-extracted content (reads from `content_items.extracted_content`), re-applies validation, rewrites extension tables.

---

## 3. Cross-Source Reconciliation Job

A daily Hatchet workflow that enforces consistency across the whole dataset.

**File:** `pipeline/workflows/reconciliation_workflow.py`

**Schedule:** `0 2 * * *` (2 AM daily)

### Checks

#### 1. Link directives referenced across sources

A MOF press release might say "per NBE Directive FXD/04/2026...". Both documents exist independently in `content_items`, but the link between them is not yet recorded.

```python
async def link_cross_source_directives(session):
    # For each article body that mentions a directive code pattern
    # Check if that directive exists in releases_docs
    # If yes → create a cross-reference record (new table: content_references)
```

#### 2. Flag orphaned amendments

```python
async def check_orphaned_amendments(session):
    orphans = await session.execute(
        select(ReleaseDoc)
        .where(ReleaseDoc.amends_directive_id.is_(None))
        .where(ReleaseDoc.directive_type_code.is_not(None))
        # find docs that mention amendment keywords but have no amends_directive_id set
    )
    for doc in orphans:
        # open backfill task: try to find the amended directive
        # log if still not found
```

#### 3. Alert on stale active sources

```python
async def check_stale_sources(session):
    threshold = datetime.utcnow() - timedelta(days=180)
    stale = await session.execute(
        select(Source)
        .join(SourceCrawlState)
        .where(Source.is_active == True)
        .where(SourceCrawlState.last_crawled_at < threshold)
    )
    for source in stale:
        await trigger_alert(source.id, reason="stale_active_source")
```

---

## 4. Operational Visibility

### Crawl job query helpers (`pipeline/utils/ops.py`)

Common queries for debugging the pipeline state:

```python
# How many URLs are pending crawl right now?
SELECT COUNT(*) FROM discovered_urls WHERE crawled_at IS NULL;

# What's the health score of each source?
SELECT s.code, scs.health_score, scs.consecutive_errors, scs.last_crawled_at
FROM sources s JOIN source_crawl_state scs ON s.id = scs.source_id;

# Failed jobs in last 24 hours
SELECT source_id, hatchet_step, error_message, started_at
FROM crawl_jobs
WHERE status = 'failed' AND started_at > NOW() - INTERVAL '24 hours';

# Content ingested per source today
SELECT s.code, COUNT(*) as items
FROM content_items ci JOIN sources s ON ci.source_id = s.id
WHERE ci.scraped_at > NOW() - INTERVAL '24 hours'
GROUP BY s.code;
```

Expose these via:
- CLI commands (`python -m pipeline.tools.status`)
- Hatchet workflow dashboard (built-in)
- Optional: simple FastAPI endpoint at `GET /ops/status`

---

## 5. GCS Storage Layout

```
gs://berhan-pipeline-raw/
├── raw_html/
│   ├── NBE/
│   │   └── 2026/05/28/
│   │       └── {url_hash_prefix}.html.gz
│   ├── MOF/
│   ├── MOR/
│   └── MOJ/
├── raw_pdfs/
│   ├── NBE/
│   │   └── fxd-04-2026.pdf
│   ├── MOF/
│   ├── MOR/
│   └── MOJ/
└── content_snapshots/
    └── {content_item_id}/
        └── v{version_number}.html.gz    ← from content_versions.raw_html_path
```

---

## Completion Checklist

- [ ] Raw HTML stored to GCS on every `fetch_page` step (verify with a real NBE crawl)
- [ ] `content_items.raw_content` contains a valid GCS path (not raw HTML inline)
- [ ] `content_versions.raw_html_path` populated on every version insert
- [ ] `replay --job-id` successfully re-extracts from stored HTML without HTTP fetch
- [ ] `replay-extraction --source-code NBE --since 2026-01-01` processes 10+ items
- [ ] Reconciliation workflow runs on schedule and produces structured log output
- [ ] Orphaned amendment check logs at least the expected cases (FXD/04/2026 → FXD/01/2024)
- [ ] Stale source alert fires correctly in test (set threshold to 1 hour temporarily)
- [ ] Ops status CLI shows pending URLs, health scores, and recent failures
