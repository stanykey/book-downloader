"""Describes BookExported protocol."""
from pathlib import Path
from typing import Protocol

from litnet_downloader.book_data import BookData
from litnet_downloader.book_data import ChapterData
from litnet_downloader.details.misc import ensure_directory_exists


class BookFormatter(Protocol):
    @staticmethod
    def filename(book: BookData) -> str:
        """Returns filename for corresponded book."""

    @staticmethod
    def prepare(chapter: ChapterData) -> str:
        """Returns content of the chapter."""


class BookExporter:
    def __init__(self, output_root: Path, exporter: BookFormatter):
        self._output_root = output_root
        self._exporter = exporter

    def dump(self, book: BookData) -> None:
        book_path = self._output_root / self._exporter.filename(book)
        ensure_directory_exists(book_path.parent)

        with open(book_path, "w", encoding="utf-8") as file:
            for chapter in book.chapters:
                file.write(self._exporter.prepare(chapter))
                file.flush()
