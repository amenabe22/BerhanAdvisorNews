import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pipeline.db.models.base import Base, UUIDPrimaryKeyMixin
from pipeline.db.models.enums import (
    ContentLanguage,
    ContentType,
    PipelineStage,
)
from pipeline.db.types import pg_enum

if TYPE_CHECKING:
    from pipeline.db.models.schedule import CrawlJob
    from pipeline.db.models.sources import Source


class ContentItem(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "content_items"

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content_type: Mapped[ContentType] = mapped_column(
        pg_enum(ContentType, "content_type"), nullable=False
    )
    language: Mapped[ContentLanguage | None] = mapped_column(
        pg_enum(ContentLanguage, "content_language"), nullable=True
    )
    canonical_url: Mapped[str] = mapped_column(Text, nullable=False)
    url_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    content_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    pipeline_stage: Mapped[PipelineStage] = mapped_column(
        pg_enum(PipelineStage, "pipeline_stage"),
        nullable=False,
        default=PipelineStage.scraped,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    sibling_document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content_items.id", ondelete="SET NULL"),
        nullable=True,
    )
    crawl_job_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crawl_jobs.id", ondelete="SET NULL"),
        nullable=True,
    )

    source: Mapped["Source"] = relationship(back_populates="content_items")
    crawl_job: Mapped["CrawlJob | None"] = relationship(
        back_populates="content_items",
    )
    sibling: Mapped["ContentItem | None"] = relationship(
        "ContentItem",
        remote_side="ContentItem.id",
        foreign_keys=[sibling_document_id],
    )
    versions: Mapped[list["ContentVersion"]] = relationship(
        back_populates="content_item",
        cascade="all, delete-orphan",
    )
    article: Mapped["Article | None"] = relationship(
        back_populates="content_item",
        uselist=False,
        cascade="all, delete-orphan",
    )
    announcement: Mapped["Announcement | None"] = relationship(
        back_populates="content_item",
        uselist=False,
        cascade="all, delete-orphan",
    )
    release_doc: Mapped["ReleaseDoc | None"] = relationship(
        back_populates="content_item",
        uselist=False,
        cascade="all, delete-orphan",
    )


class ContentVersion(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "content_versions"

    content_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    content_hash: Mapped[str] = mapped_column(Text, nullable=False)
    title_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachments_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    diff_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_html_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    content_item: Mapped["ContentItem"] = relationship(back_populates="versions")


class Article(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "articles"

    content_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content_items.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    word_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    content_item: Mapped["ContentItem"] = relationship(back_populates="article")


class Announcement(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "announcements"

    content_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content_items.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    institution_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    announcement_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reference_number: Mapped[str | None] = mapped_column(String(128), nullable=True)

    content_item: Mapped["ContentItem"] = relationship(back_populates="announcement")


class ReleaseDoc(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "releases_docs"

    content_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content_items.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    directive_type_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    directive_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    directive_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pdf_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_pdf_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    amends_directive_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("releases_docs.id", ondelete="SET NULL"),
        nullable=True,
    )
    repealed_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("releases_docs.id", ondelete="SET NULL"),
        nullable=True,
    )

    content_item: Mapped["ContentItem"] = relationship(back_populates="release_doc")
    amends_directive: Mapped["ReleaseDoc | None"] = relationship(
        "ReleaseDoc",
        remote_side="ReleaseDoc.id",
        foreign_keys=[amends_directive_id],
    )
    repealed_by: Mapped["ReleaseDoc | None"] = relationship(
        "ReleaseDoc",
        remote_side="ReleaseDoc.id",
        foreign_keys=[repealed_by_id],
    )
