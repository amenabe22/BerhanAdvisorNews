import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pipeline.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from pipeline.db.models.enums import HatchetWorkflow, JobStatus
from pipeline.db.types import pg_enum

if TYPE_CHECKING:
    from pipeline.db.models.content import ContentItem
    from pipeline.db.models.sources import Source
    from pipeline.db.models.urls import DiscoveredUrl


class CrawlSchedule(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "crawl_schedule"

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
    )
    cron_expression: Mapped[str] = mapped_column(String(64), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_paused: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    workflow_type: Mapped[HatchetWorkflow] = mapped_column(
        pg_enum(HatchetWorkflow, "hatchet_workflow"), nullable=False
    )

    source: Mapped["Source"] = relationship(back_populates="crawl_schedules")


class CrawlJob(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "crawl_jobs"

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
    )
    hatchet_run_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    hatchet_workflow_type: Mapped[HatchetWorkflow] = mapped_column(
        pg_enum(HatchetWorkflow, "hatchet_workflow"), nullable=False
    )
    hatchet_step: Mapped[str | None] = mapped_column(String(128), nullable=True)
    worker_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[JobStatus] = mapped_column(
        pg_enum(JobStatus, "job_status"),
        nullable=False,
        default=JobStatus.pending,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    stats: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    source: Mapped["Source"] = relationship(back_populates="crawl_jobs")
    discovered_urls: Mapped[list["DiscoveredUrl"]] = relationship(
        back_populates="crawl_job",
    )
    content_items: Mapped[list["ContentItem"]] = relationship(
        back_populates="crawl_job",
    )
