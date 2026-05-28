# BerhanAdvisorNews — Ethiopia Intelligence Pipeline

Government and news ingestion pipeline for Ethiopian federal sources (NBE, MOF, MOR, MOJ).

## Quick start (Phase 1)

```bash
# 1. Dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Environment
cp .env.example .env

# 3. Infrastructure
docker compose up -d db
# Wait for Postgres healthy, then:
docker compose up -d hatchet-lite

# 4. Database schema
export DATABASE_URL_SYNC=postgresql://postgres:password@localhost:5432/berhan_pipeline
alembic upgrade head

# If migration failed partway, reset and retry:
# psql "$DATABASE_URL_SYNC" -f scripts/reset_pipeline_db.sql
# alembic upgrade head

# 5. Seed sources
python scripts/seed_sources.py
```

- **Postgres:** `localhost:5432` / database `berhan_pipeline`
- **Hatchet dashboard:** http://localhost:8888 (see `docker-compose.yml` for admin credentials)

## Project layout

```
pipeline/           # Application code
docs/pipeline/      # Phase-by-phase build plans
scripts/            # seed_sources.py, DB init
alembic.ini         # Migrations (pipeline/db/migrations)
docker-compose.yml  # Postgres + Hatchet Lite
```

## Build phases

See [docs/pipeline/README.md](docs/pipeline/README.md) for the full 8-phase plan.
