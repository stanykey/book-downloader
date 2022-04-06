"""Contains book related entities."""

from dataclasses import dataclass, field


@dataclass
class Chapter:
    id: str
    title: str
    content: str = ''


@dataclass
class Book:
    author: str
    title: str
    chapters: list[Chapter] = field(default_factory=list)
