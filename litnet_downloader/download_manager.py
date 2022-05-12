"""Literally, DownloadManager is the main class."""
from asyncio import run as run_coroutine
from functools import cache
from pathlib import Path

from litnet_downloader.book_data import BookData
from litnet_downloader.book_data import ChapterData
from litnet_downloader.details.book_downloader import BookDownloader
from litnet_downloader.details.metadata import BookMetadata
from litnet_downloader.details.misc import ensure_directory_exists
from litnet_downloader.details.misc import fingerprint
from litnet_downloader.details.misc import remove_directory


class DownloadManager:
    def __init__(self, token: str, pem_path: Path | None = None):
        self._downloader = BookDownloader(token, pem_path)

        self._cached_book_data: set[Path] = set()

    def get_book(self, book_url: str, /, use_cache: bool = True, clean_after: bool = True) -> BookData:
        book_dir = self._get_working_directory(book_url, clean=not use_cache)

        metadata: BookMetadata = run_coroutine(self._downloader.download(book_url, book_dir))
        book: BookData = self._make_book(metadata)

        if clean_after:
            self._remove_from_cache(book_dir)

        return book

    @classmethod
    @cache
    def cache_location(cls) -> Path:
        return Path(__file__).parent.resolve() / ".cache"

    def reset_cache(self) -> None:
        for book_dir in list(self._cached_book_data):
            self._remove_from_cache(book_dir)

    def _get_working_directory(self, book_url: str, clean: bool) -> Path:
        book_path = self._compose_book_path(book_url)
        if book_path.exists() and clean:
            remove_directory(book_path)

        self._add_to_cache(book_path)

        return book_path

    def _add_to_cache(self, book_dir: Path) -> None:
        ensure_directory_exists(book_dir)
        self._cached_book_data.add(book_dir)

    def _remove_from_cache(self, book_dir: Path) -> None:
        remove_directory(book_dir)
        self._cached_book_data.discard(book_dir)

    @staticmethod
    def _make_book(meta: BookMetadata) -> BookData:
        book = BookData(
            author=meta.author,
            title=meta.title,
            chapters=[ChapterData(info.title, info.load_content()) for info in meta.chapters],
        )
        return book

    @classmethod
    def _compose_book_path(cls, book_url: str) -> Path:
        book_dir_name = fingerprint(book_url)
        return cls.cache_location() / book_dir_name