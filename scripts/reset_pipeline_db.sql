-- Full reset of pipeline schema (tables + enums + alembic tracking).
-- Usage: psql "$DATABASE_URL_SYNC" -f scripts/reset_pipeline_db.sql

DROP TABLE IF EXISTS releases_docs CASCADE;
DROP TABLE IF EXISTS announcements CASCADE;
DROP TABLE IF EXISTS articles CASCADE;
DROP TABLE IF EXISTS content_versions CASCADE;
DROP TABLE IF EXISTS content_items CASCADE;
DROP TABLE IF EXISTS discovered_urls CASCADE;
DROP TABLE IF EXISTS crawl_jobs CASCADE;
DROP TABLE IF EXISTS crawl_schedule CASCADE;
DROP TABLE IF EXISTS source_crawl_state CASCADE;
DROP TABLE IF EXISTS sources CASCADE;
DROP TABLE IF EXISTS alembic_version CASCADE;

DROP TYPE IF EXISTS pipeline_stage CASCADE;
DROP TYPE IF EXISTS job_status CASCADE;
DROP TYPE IF EXISTS hatchet_workflow CASCADE;
DROP TYPE IF EXISTS content_type CASCADE;
DROP TYPE IF EXISTS source_category CASCADE;
DROP TYPE IF EXISTS source_type CASCADE;
DROP TYPE IF EXISTS content_language CASCADE;
