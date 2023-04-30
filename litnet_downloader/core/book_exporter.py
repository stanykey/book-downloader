"""Describes BookExported protocol."""
from pathlib import Path
from typing import Protocol

from aiofiles import open

from litnet_downloader.core.book_data import BookData
from litnet_downloader.core.book_data import ChapterData
from litnet_downloader.internal.misc import ensure_directory_exists


class BookFormatter(Protocol):
    @staticmethod
    def filename(book: BookData) -> str:
        """Returns filename for corresponded book."""

    @staticmethod
    def prepare(chapter: ChapterData) -> str:
        """Returns content of the chapter."""


class BookExporter:
    def __init__(self, working_dir: Path, formatter: BookFormatter):
        self._working_dir = working_dir
        self._formatter = formatter

    async def dump(self, book: BookData) -> None:
        book_path = self._working_dir / self._formatter.filename(book)
        ensure_directory_exists(book_path.parent)

        async with open(book_path, "w", encoding="utf-8") as file:
            for chapter in book.chapters:
                await file.write(self._formatter.prepare(chapter))
                await file.flush()
