"""Literally, DownloadManager is the main class."""
from asyncio import run
from asyncio import set_event_loop_policy
from asyncio import WindowsSelectorEventLoopPolicy
from functools import cached_property
from pathlib import Path
from platform import system
from ssl import create_default_context
from tempfile import gettempdir

from litnet_downloader.core.book_data import BookData
from litnet_downloader.core.book_data import ChapterData
from litnet_downloader.internal.book_downloader import BookDownloader
from litnet_downloader.internal.metadata import BookMetadata
from litnet_downloader.internal.misc import ensure_directory_exists
from litnet_downloader.internal.misc import fingerprint
from litnet_downloader.internal.misc import remove_directory


class DownloadManager:
    def __init__(self, token: str, working_dir: Path, *, pem_path: Path | None = None) -> None:
        self._working_dir = working_dir
        self._ssl_context = create_default_context(cafile=pem_path)
        self._downloader = BookDownloader(token, self._ssl_context)

        self._cached_book_data: set[Path] = set()

        # it's a bit dirty but currently 1 of 2 possible workarounds
        # https://github.com/aio-libs/aiohttp/issues/4324
        if system() == "Windows":
            set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    def get_book(self, book_url: str, /, use_cache: bool = True) -> BookData:
        book_dir = self._get_working_directory(book_url, use_cache)
        try:
            metadata: BookMetadata = run(self._downloader.download(book_url, book_dir))
            book: BookData = self._make_book(metadata)
        finally:
            if not use_cache:
                remove_directory(book_dir)

        return book

    @cached_property
    def cache_location(self) -> Path:
        return self._working_dir / ".downloads-cache"

    def reset_cache(self) -> None:
        for book_dir in list(self._cached_book_data):
            self._remove_from_cache(book_dir)

    def _get_working_directory(self, book_url: str, use_cache: bool) -> Path:
        if not use_cache:
            working_dir = Path(gettempdir()).resolve()
            return self._compose_book_path(working_dir, book_url)

        book_path = self._compose_book_path(self.cache_location, book_url)
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

    @staticmethod
    def _compose_book_path(parent: Path, book_url: str) -> Path:
        book_dir_name = fingerprint(book_url)
        return parent / book_dir_name
