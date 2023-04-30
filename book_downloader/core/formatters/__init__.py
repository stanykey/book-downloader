"""Book formatters."""
from enum import auto
from enum import StrEnum

from book_downloader.core.formatters.txt import TextFormatter


class BookFormat(StrEnum):
    txt = auto()
    epub = auto()
    fb2 = auto()
    default = txt


__all__ = ("BookFormat", "TextFormatter")
