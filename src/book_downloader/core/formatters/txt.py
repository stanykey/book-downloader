"""Basically, the default formatter."""

from bs4 import BeautifulSoup

from book_downloader.core.book_data import BookData
from book_downloader.core.book_data import ChapterData


class TextFormatter:
    @staticmethod
    def filename(book: BookData) -> str:
        author = TextFormatter._sanitize_filename_part(book.author)
        title = TextFormatter._sanitize_filename_part(book.title)
        return f"[{author}]{title}.txt"

    @staticmethod
    def prepare(chapter: ChapterData) -> str:
        text_blocks = [chapter.title]

        soup = BeautifulSoup(chapter.content, "lxml")
        text_blocks.extend(block.get_text() for block in soup.find_all("p"))
        text_blocks.append("\n\n")

        return "\n\n".join(text_blocks)

    @staticmethod
    def _sanitize_filename_part(value: str) -> str:
        invalid_chars = '<>:"/\\|?*'
        sanitized = "".join("_" if (ch in invalid_chars or ord(ch) < 32) else ch for ch in value)
        sanitized = sanitized.strip(" .")

        if not sanitized:
            return "unknown"

        return sanitized
