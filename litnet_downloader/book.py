"""Contains book related entities."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Chapter:
    id: str
    title: str
    location: field(default_factory=Path)

    @property
    def downloaded(self) -> bool:
        return self.location.exists() and self.location.is_file()


@dataclass
class Book:
    author: str
    title: str
    chapters: list[Chapter] = field(default_factory=list)
