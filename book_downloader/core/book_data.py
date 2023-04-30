"""Contains book related entities."""
from dataclasses import dataclass
from dataclasses import field


@dataclass
class ChapterData:
    """Represents raw chapter's data."""

    title: str = ""
    content: str = ""


@dataclass
class BookData:
    """Represents raw book's data."""

    author: str = ""
    title: str = ""
    chapters: list[ChapterData] = field(default_factory=list)
