"""Initial pipeline schema.

Revision ID: 001
Revises:
Create Date: 2026-05-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# postgresql.ENUM + create_type=False: create once in upgrade(), not again on create_table.
_ENUM = postgresql.ENUM

content_language = _ENUM(
    "am", "en", "om", "ti", "so", "mixed", name="content_language", create_type=False
)
source_type = _ENUM(
    "website", "rss", "api", "pdf_portal", "social", name="source_type", create_type=False
)
source_category = _ENUM(
    "legal",
    "finance",
    "politics",
    "business",
    "general_news",
    "government",
    "regional",
    "international",
    name="source_category",
    create_type=False,
)
content_type = _ENUM(
    "article",
    "release",
    "announcement",
    "proclamation",
    "document",
    "press_release",
    name="content_type",
    create_type=False,
)
hatchet_workflow = _ENUM(
    "spider", "crawler", name="hatchet_workflow", create_type=False
)
job_status = _ENUM(
    "pending",
    "running",
    "completed",
    "failed",
    "skipped",
    "retrying",
    name="job_status",
    create_type=False,
)
pipeline_stage = _ENUM(
    "scraped",
    "processed",
    "ingested",
    "published",
    name="pipeline_stage",
    create_type=False,
)


def upgrade() -> None:
    content_language.create(op.get_bind(), checkfirst=True)
    source_type.create(op.get_bind(), checkfirst=True)
    source_category.create(op.get_bind(), checkfirst=True)
    content_type.create(op.get_bind(), checkfirst=True)
    hatchet_workflow.create(op.get_bind(), checkfirst=True)
    job_status.create(op.get_bind(), checkfirst=True)
    pipeline_stage.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("source_type", source_type, nullable=False),
        sa.Column("category", source_category, nullable=False),
        sa.Column("default_language", content_language, nullable=False),
        sa.Column("selectors", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("crawl_delay_ms", sa.Integer(), nullable=False, server_default="2000"),
        sa.Column(
            "max_concurrent_requests", sa.Integer(), nullable=False, server_default="2"
        ),
        sa.Column(
            "request_timeout_ms", sa.Integer(), nullable=False, server_default="60000"
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "source_crawl_state",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("last_crawled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_crawl_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "consecutive_errors", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("health_score", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("crawl_config", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id"),
    )

    op.create_table(
        "crawl_schedule",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cron_expression", sa.String(length=64), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_paused", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("workflow_type", hatchet_workflow, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "crawl_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hatchet_run_id", sa.String(length=128), nullable=True),
        sa.Column("hatchet_workflow_type", hatchet_workflow, nullable=False),
        sa.Column("hatchet_step", sa.String(length=128), nullable=True),
        sa.Column("worker_id", sa.String(length=128), nullable=True),
        sa.Column("status", job_status, nullable=False, server_default="pending"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("stats", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "discovered_urls",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("normalized_url", sa.Text(), nullable=False),
        sa.Column("url_hash", sa.Text(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("link_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "discovered_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("crawled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("crawl_job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["crawl_job_id"], ["crawl_jobs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url_hash"),
    )
    op.create_index("ix_discovered_urls_source_id", "discovered_urls", ["source_id"])
    op.create_index("ix_discovered_urls_url_hash", "discovered_urls", ["url_hash"])

    op.create_table(
        "content_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content_type", content_type, nullable=False),
        sa.Column("language", content_language, nullable=True),
        sa.Column("canonical_url", sa.Text(), nullable=False),
        sa.Column("url_hash", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.Text(), nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("raw_content", sa.Text(), nullable=True),
        sa.Column("extracted_content", sa.Text(), nullable=True),
        sa.Column(
            "pipeline_stage",
            pipeline_stage,
            nullable=False,
            server_default="scraped",
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "scraped_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("sibling_document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("crawl_job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["sibling_document_id"], ["content_items.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["crawl_job_id"], ["crawl_jobs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url_hash"),
    )
    op.create_index("ix_content_items_source_id", "content_items", ["source_id"])
    op.create_index("ix_content_items_url_hash", "content_items", ["url_hash"])

    op.create_table(
        "content_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("content_hash", sa.Text(), nullable=False),
        sa.Column("title_hash", sa.Text(), nullable=True),
        sa.Column("body_hash", sa.Text(), nullable=True),
        sa.Column("attachments_hash", sa.Text(), nullable=True),
        sa.Column("diff_summary", sa.Text(), nullable=True),
        sa.Column("raw_html_path", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["content_item_id"], ["content_items.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("content_item_id", "version", name="uq_content_item_version"),
    )
    op.create_index(
        "ix_content_versions_content_item_id",
        "content_versions",
        ["content_item_id"],
    )

    op.create_table(
        "articles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=True),
        sa.Column("excerpt", sa.Text(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("word_count", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["content_item_id"], ["content_items.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("content_item_id"),
    )

    op.create_table(
        "announcements",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("institution_code", sa.String(length=32), nullable=True),
        sa.Column("announcement_type", sa.String(length=64), nullable=True),
        sa.Column("reference_number", sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(
            ["content_item_id"], ["content_items.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("content_item_id"),
    )

    op.create_table(
        "releases_docs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("directive_type_code", sa.String(length=32), nullable=True),
        sa.Column("directive_number", sa.String(length=32), nullable=True),
        sa.Column("directive_year", sa.Integer(), nullable=True),
        sa.Column("pdf_url", sa.Text(), nullable=True),
        sa.Column("raw_pdf_path", sa.Text(), nullable=True),
        sa.Column("ocr_text", sa.Text(), nullable=True),
        sa.Column("amends_directive_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("repealed_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["content_item_id"], ["content_items.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["amends_directive_id"], ["releases_docs.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["repealed_by_id"], ["releases_docs.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("content_item_id"),
    )


def downgrade() -> None:
    op.drop_table("releases_docs")
    op.drop_table("announcements")
    op.drop_table("articles")
    op.drop_index("ix_content_versions_content_item_id", table_name="content_versions")
    op.drop_table("content_versions")
    op.drop_index("ix_content_items_url_hash", table_name="content_items")
    op.drop_index("ix_content_items_source_id", table_name="content_items")
    op.drop_table("content_items")
    op.drop_index("ix_discovered_urls_url_hash", table_name="discovered_urls")
    op.drop_index("ix_discovered_urls_source_id", table_name="discovered_urls")
    op.drop_table("discovered_urls")
    op.drop_table("crawl_jobs")
    op.drop_table("crawl_schedule")
    op.drop_table("source_crawl_state")
    op.drop_table("sources")

    pipeline_stage.drop(op.get_bind(), checkfirst=True)
    job_status.drop(op.get_bind(), checkfirst=True)
    hatchet_workflow.drop(op.get_bind(), checkfirst=True)
    content_type.drop(op.get_bind(), checkfirst=True)
    source_category.drop(op.get_bind(), checkfirst=True)
    source_type.drop(op.get_bind(), checkfirst=True)
    content_language.drop(op.get_bind(), checkfirst=True)
