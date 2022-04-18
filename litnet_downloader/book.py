"""Contains book related entities."""
from dataclasses import dataclass
from dataclasses import field


@dataclass
class Chapter:
    title: str = ""
    content: str = ""


@dataclass
class Book:
    author: str = ""
    title: str = ""
    chapters: list[Chapter] = field(default_factory=list)
