import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pipeline.db.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from pipeline.db.models.schedule import CrawlJob
    from pipeline.db.models.sources import Source


class DiscoveredUrl(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "discovered_urls"

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    normalized_url: Mapped[str] = mapped_column(Text, nullable=False)
    url_hash: Mapped[str] = mapped_column(
        Text, unique=True, nullable=False, index=True
    )
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    link_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    crawled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    crawl_job_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crawl_jobs.id", ondelete="SET NULL"),
        nullable=True,
    )

    source: Mapped["Source"] = relationship(back_populates="discovered_urls")
    crawl_job: Mapped["CrawlJob | None"] = relationship(
        back_populates="discovered_urls",
    )
