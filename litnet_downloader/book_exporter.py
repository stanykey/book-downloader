"""Describes BookExported protocol."""
from pathlib import Path
from typing import Protocol

from litnet_downloader.book import Book
from litnet_downloader.book import Chapter


class BookFormatter(Protocol):
    @staticmethod
    def filename(book: Book) -> str:
        """Returns filename for corresponded book."""

    @staticmethod
    def prepare(chapter: Chapter) -> str:
        """Returns content of the chapter."""


class BookExporter:
    def __init__(self, output_root: Path, exporter: BookFormatter):
        self._output_root = output_root
        self._exporter = exporter

    def dump(self, book: Book) -> None:
        book_path = self._output_root / self._exporter.filename(book)
        with open(book_path, "w", encoding="utf-8") as file:
            for chapter in book.chapters:
                file.write(self._exporter.prepare(chapter))
                file.flush()
