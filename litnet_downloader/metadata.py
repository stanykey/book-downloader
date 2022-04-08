"""Contains data classes that represent book-related metadata."""

from dataclasses import dataclass, field
from json import dump as save_json, load as load_json, JSONDecodeError
from pathlib import Path
from typing import Any


@dataclass
class ChapterMetadata:
    id: str
    title: str
    content_path: Path = field(default_factory=Path)

    def __post_init__(self):
        if not isinstance(self.content_path, Path):
            self.content_path = Path(self.content_path)

    @property
    def downloaded(self) -> bool:
        return self.content_path and self.content_path.exists() and self.content_path.is_file()

    def load_content(self) -> str:
        if not self.downloaded:
            return ''

        with open(self.content_path, 'r', encoding='utf-8') as file:
            return file.read()

    def to_json(self) -> dict[str, Any]:
        json = dict(
            id=self.id,
            title=self.title,
            content_path=str(self.content_path)
        )
        return json


@dataclass
class BookMetadata:
    working_dir: Path

    csrf: str = ''
    author: str = ''
    title: str = ''
    chapters: list[ChapterMetadata] = field(default_factory=list)

    @property
    def completed(self) -> bool:
        return all([self.csrf, self.author, self.title, self.chapters])

    @property
    def file_path(self) -> Path:
        return self.working_dir / 'metadata.json'

    def save(self) -> None:
        with open(self.file_path, 'w', encoding='utf-8') as file:
            save_json(self.to_json(), file, sort_keys=True, indent=4)

    def load(self) -> bool:
        if not self.file_path.exists():
            return False

        with open(self.file_path, 'r', encoding='utf-8') as file:
            try:
                json: dict[str, Any] = load_json(file)
            except JSONDecodeError:
                return False

        self.csrf = json.get('csrf', '')
        self.author = json.get('author', '')
        self.title = json.get('title', '')
        self.chapters = [ChapterMetadata(**item) for item in json.get('chapters', [])]

        return True

    def to_json(self) -> dict[str, Any]:
        json = dict(
            csrf=self.csrf,
            author=self.author,
            title=self.title,
            chapters=[chapter.to_json() for chapter in self.chapters]
        )
        return json
    