import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func

from pipeline.db.types import pg_enum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pipeline.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from pipeline.db.models.enums import ContentLanguage, SourceCategory, SourceType

if TYPE_CHECKING:
    from pipeline.db.models.content import ContentItem
    from pipeline.db.models.schedule import CrawlJob, CrawlSchedule
    from pipeline.db.models.urls import DiscoveredUrl


class Source(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "sources"

    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[SourceType] = mapped_column(
        pg_enum(SourceType, "source_type"), nullable=False
    )
    category: Mapped[SourceCategory] = mapped_column(
        pg_enum(SourceCategory, "source_category"), nullable=False
    )
    default_language: Mapped[ContentLanguage] = mapped_column(
        pg_enum(ContentLanguage, "content_language"), nullable=False
    )
    selectors: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    crawl_delay_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=2000)
    max_concurrent_requests: Mapped[int] = mapped_column(
        Integer, nullable=False, default=2
    )
    request_timeout_ms: Mapped[int] = mapped_column(
        Integer, nullable=False, default=60000
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    crawl_state: Mapped["SourceCrawlState | None"] = relationship(
        back_populates="source",
        uselist=False,
        cascade="all, delete-orphan",
    )
    crawl_schedules: Mapped[list["CrawlSchedule"]] = relationship(
        back_populates="source",
        cascade="all, delete-orphan",
    )
    crawl_jobs: Mapped[list["CrawlJob"]] = relationship(
        back_populates="source",
        cascade="all, delete-orphan",
    )
    discovered_urls: Mapped[list["DiscoveredUrl"]] = relationship(
        back_populates="source",
        cascade="all, delete-orphan",
    )
    content_items: Mapped[list["ContentItem"]] = relationship(
        back_populates="source",
        cascade="all, delete-orphan",
    )


class SourceCrawlState(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "source_crawl_state"

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    last_crawled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_crawl_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    consecutive_errors: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    health_score: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    crawl_config: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    source: Mapped["Source"] = relationship(back_populates="crawl_state")
