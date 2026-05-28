-- Run if `alembic upgrade head` failed partway (enum types exist but tables may not).
-- Usage: psql "$DATABASE_URL_SYNC" -f scripts/reset_migration_enums.sql

DROP TYPE IF EXISTS pipeline_stage CASCADE;
DROP TYPE IF EXISTS job_status CASCADE;
DROP TYPE IF EXISTS hatchet_workflow CASCADE;
DROP TYPE IF EXISTS content_type CASCADE;
DROP TYPE IF EXISTS source_category CASCADE;
DROP TYPE IF EXISTS source_type CASCADE;
DROP TYPE IF EXISTS content_language CASCADE;

DROP TABLE IF EXISTS alembic_version CASCADE;
