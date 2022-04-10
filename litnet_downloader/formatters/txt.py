"""Basically, the default formatter."""
from bs4 import BeautifulSoup

from litnet_downloader.book import Book
from litnet_downloader.book import Chapter


class TextFormatter:
    @staticmethod
    def filename(book: Book) -> str:
        return f"[{book.author}]{book.title}.txt"

    @staticmethod
    def prepare(chapter: Chapter) -> str:
        text_blocks = [chapter.title]

        text_blocks.extend(block.get_text() for block in BeautifulSoup(chapter.content).find_all("p"))
        text_blocks.append("\n\n")

        return "\n\n".join(text_blocks)
