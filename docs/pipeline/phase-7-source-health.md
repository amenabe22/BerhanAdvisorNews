# Phase 7 — Source Health System

**Week:** 5  
**Goal:** Automatically track source reliability, degrade and pause failing sources, and run daily canary checks to detect silent extraction breakages.  
**Depends on:** Phase 1 (`source_crawl_state` table), Phase 6 (Hatchet workflows call health updaters)

---

## Deliverables

- [ ] Health score update logic (+10 / -20)
- [ ] Auto-pause trigger when health_score <= 0
- [ ] Manual resume mechanism
- [ ] Daily canary check workflow
- [ ] Failure-mode alert hooks
- [ ] Per-source error log in `crawl_jobs`

---

## Why This Is Built Early

Ethiopian government sites:
- Break often (server errors, especially MOJ FIRMA)
- Timeout often (MOR Liferay under load)
- Redesign without notice (selectors break silently)
- Change URL structures (NBE did exactly this with `/nbe_news/` vs `/news/`)

Without source health tracking, a failing source will exhaust workers with endless retries and never surface the problem.

---

## Health Score Logic

Built into `source_crawl_state.health_score`.

| Event | Score delta |
|-------|-------------|
| Successful crawl (any URL fetched + extracted) | +10 |
| Failed crawl (HTTP error, timeout, extraction failure) | -20 |
| Score floor | 0 (cannot go below 0) |
| Score ceiling | 100 (starting value, max) |
| Auto-pause threshold | health_score <= 0 |

```python
async def update_source_health(session, source_id: UUID, success: bool):
    state = await session.get(SourceCrawlState, source_id)

    if success:
        state.health_score = min(100, state.health_score + 10)
        state.consecutive_errors = 0
    else:
        state.health_score = max(0, state.health_score - 20)
        state.consecutive_errors += 1

    state.last_crawled_at = datetime.utcnow()

    if state.health_score <= 0:
        await auto_pause_source(session, source_id)
        await trigger_alert(source_id, reason="health_score_zero")

    await session.commit()
```

---

## Auto-Pause Mechanism

When `health_score` reaches 0:
1. Set `crawl_schedule.is_paused = True` for all schedule rows for this source
2. Trigger an alert (log + optional webhook/email)
3. Log the pause event in `crawl_jobs` with `status=skipped`

```python
async def auto_pause_source(session, source_id: UUID):
    await session.execute(
        update(CrawlSchedule)
        .where(CrawlSchedule.source_id == source_id)
        .values(is_paused=True)
    )
    logger.error(f"Source {source_id} auto-paused: health_score reached 0")
```

The Hatchet spider/crawler workflows check `crawl_schedule.is_paused` at the start of `fetch_source` and exit early if paused.

---

## Manual Resume

Provide a CLI command and/or API endpoint to resume a paused source:

```python
# CLI: python -m pipeline.tools.resume_source --source-code NBE
async def resume_source(source_code: str, reset_health_to: int = 50):
    async with get_session() as session:
        source = await session.execute(
            select(Source).where(Source.code == source_code)
        )
        source = source.scalar_one()

        await session.execute(
            update(CrawlSchedule)
            .where(CrawlSchedule.source_id == source.id)
            .values(is_paused=False)
        )
        state = await session.get(SourceCrawlState, source.id)
        state.health_score = reset_health_to
        state.consecutive_errors = 0
        await session.commit()

    logger.info(f"Source {source_code} resumed with health_score={reset_health_to}")
```

Reset to 50 (not 100) so the source is still in a cautious state and will auto-pause again quickly if errors continue.

---

## Daily Canary Check

A separate lightweight Hatchet workflow that runs daily per source against known-stable URLs.

**File:** `pipeline/workflows/canary_workflow.py`

### What it checks

For each source, 3–5 URLs that are known to always exist and be extractable:

```python
# Store in sources.selectors JSONB
"canary_urls": [
    "https://nbe.gov.et/nbe_news/authorization-for-commercial-banks-to-issue-export-permits-for-exports-to-the-peoples-republic-of-china/",
    "https://nbe.gov.et/files/fxd-04-2026/",
    "https://nbe.gov.et/news/press-release/"
]
```

### Canary logic

```python
@hatchet.step()
async def run_canary(self, ctx: Context) -> dict:
    source_id = ctx.workflow_input()["source_id"]
    source = await get_source(source_id)
    canary_urls = source.selectors.get("canary_urls", [])

    results = []
    for url in canary_urls:
        try:
            resp = await fetcher.fetch(url)
            extractor = get_extractor(source.code)
            extracted = extractor.extract(resp.text, url)
            ok = bool(extracted and extracted.title and extracted.content)
        except Exception as e:
            ok = False

        results.append({"url": url, "ok": ok})

    success_rate = sum(1 for r in results if r["ok"]) / max(len(results), 1)

    if success_rate < 1.0:
        await trigger_alert(source_id, reason=f"canary_failure: {success_rate:.0%} success")
        await update_source_health(session, source_id, success=False)

    return {"success_rate": success_rate, "results": results}
```

**Fail loudly:** If any canary URL fails extraction, alert immediately. A broken canary means the extractor is broken for the whole source — not just one article.

---

## Alert Hooks (`pipeline/utils/alerts.py`)

Start simple — structured log + optional webhook. Upgrade to email/Slack later.

```python
import logging

alert_logger = logging.getLogger("pipeline.alerts")

async def trigger_alert(source_id: UUID, reason: str, extra: dict = None):
    alert_logger.error(
        "PIPELINE_ALERT",
        extra={
            "source_id": str(source_id),
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            **(extra or {}),
        }
    )
    # Optional: POST to webhook URL from env var
    webhook_url = os.getenv("ALERT_WEBHOOK_URL")
    if webhook_url:
        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json={
                "source_id": str(source_id),
                "reason": reason,
            })
```

Alert conditions:
- `health_score_zero` — source auto-paused
- `canary_failure` — extractor broken for known-stable URL
- `source_down_2_cycles` — source failed 2 consecutive schedule cycles
- `selector_returned_null` — extraction returned empty title or body

---

## Failure-Mode Playbook

Embed as comments in source config or as a reference doc:

| Symptom | Likely Cause | Action |
|---------|-------------|--------|
| NBE health dropping | Elementor update changed CSS classes | Update `title_selector`, `body_selector` in `sources.selectors`; resume |
| MOJ health = 0 | FIRMA backend instability | Check if site is up manually; wait 24h; resume if restored |
| MOR canary failing | Liferay update or robots.txt change | Check robots.txt; switch to Playwright fallback if needed |
| MOF canary failing | Django/Mezzanine template change | Update `body_selector`; test against canary URL locally |
| All sources degrading | IP block or network issue | Check connectivity; rotate IP if proxy available |

---

## Completion Checklist

- [ ] `update_source_health` called at end of every spider + crawler workflow run
- [ ] Health score increments on success, decrements on failure (floor 0)
- [ ] Source auto-pauses when health_score hits 0
- [ ] `crawl_schedule.is_paused` checked at start of `fetch_source` step
- [ ] Manual resume CLI command works and resets health to 50
- [ ] Canary workflow registered and scheduled daily (cron: `0 6 * * *`)
- [ ] Canary failure triggers alert log entry
- [ ] 3–5 canary URLs configured in `sources.selectors` for each of the 4 sources
