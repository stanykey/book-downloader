"""Provide the `Service` protocol and implementations."""
from enum import StrEnum
from typing import Any
from typing import Protocol

from book_downloader.core.download_manager import BookDownloader


class ServiceId(StrEnum):
    Litnet = "litnet.com"


class Service(Protocol):
    @classmethod
    def host(cls) -> str:
        """Return service host."""
        ...

    @classmethod
    async def check_service(cls) -> bool:
        """Check/ping service."""
        ...

    @classmethod
    async def check_url(cls, url: str) -> bool:
        """Check the accessibility of url."""
        ...

    @classmethod
    def canonical_book_url(cls, url: str) -> str:
        """Return a well-formed book root URL or an empty string if impossible."""
        ...

    def get_downloader(self) -> BookDownloader:
        """Get a downloader that knows how to download a book."""
        ...


def make_service(service_id: ServiceId, *args: Any, **kwargs: Any) -> Service | None:
    """Factory method creates service by `id` with provided additional arguments."""
    return None
