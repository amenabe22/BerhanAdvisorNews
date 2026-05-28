from abc import ABC, abstractmethod

from pipeline.db.models.sources import Source


class SpiderAdapter(ABC):
    """Discover raw URLs from a source. Normalization happens outside adapters."""

    @abstractmethod
    async def discover_urls(self, source: Source) -> list[str]:
        """Return un-normalized absolute URLs."""
