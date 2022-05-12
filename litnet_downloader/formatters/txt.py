"""Basically, the default formatter."""
from bs4 import BeautifulSoup

from litnet_downloader.book_data import BookData
from litnet_downloader.book_data import ChapterData


class TextFormatter:
    @staticmethod
    def filename(book: BookData) -> str:
        return f"[{book.author}]{book.title}.txt"

    @staticmethod
    def prepare(chapter: ChapterData) -> str:
        text_blocks = [chapter.title]

        soup = BeautifulSoup(chapter.content, "lxml")
        text_blocks.extend(block.get_text() for block in soup.find_all("p"))
        text_blocks.append("\n\n")

        return "\n\n".join(text_blocks)
