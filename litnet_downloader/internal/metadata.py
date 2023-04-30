"""Contains data classes that represent book-related metadata."""
from dataclasses import dataclass
from dataclasses import field
from json import dumps
from json import JSONDecodeError
from json import loads
from pathlib import Path
from typing import Any

from aiofiles import open


@dataclass
class ChapterMetadata:
    id: str
    title: str
    content_path: Path = field(default_factory=Path)

    def __post_init__(self) -> None:
        if not isinstance(self.content_path, Path):
            self.content_path = Path(self.content_path)

    @property
    def downloaded(self) -> bool:
        return self.content_path.exists() and self.content_path.is_file()

    async def load_content(self) -> str:
        if not self.downloaded:
            return ""

        async with open(self.content_path, encoding="utf-8") as file:
            return await file.read()

    def to_json(self) -> dict[str, Any]:
        json = dict(id=self.id, title=self.title, content_path=str(self.content_path))
        return json


@dataclass
class BookMetadata:
    working_dir: Path

    csrf: str = ""
    author: str = ""
    title: str = ""
    chapters: list[ChapterMetadata] = field(default_factory=list)

    @property
    def completed(self) -> bool:
        return all([self.csrf, self.author, self.title, self.chapters])

    @property
    def file_path(self) -> Path:
        return self.working_dir / "metadata.json"

    async def save(self) -> None:
        async with open(self.file_path, "w", encoding="utf-8") as file:
            json = dumps(self.to_json(), sort_keys=True, indent=4)
            await file.write(json)
            await file.flush()

    async def load(self) -> bool:
        if not self.file_path.exists():
            return False

        async with open(self.file_path, encoding="utf-8") as file:
            file_content = await file.read()
            try:
                json = loads(file_content)
            except JSONDecodeError:
                return False

        self.csrf = json.get("csrf", "")
        self.author = json.get("author", "")
        self.title = json.get("title", "")
        self.chapters = [ChapterMetadata(**item) for item in json.get("chapters", [])]

        return True

    def to_json(self) -> dict[str, Any]:
        json = dict(
            csrf=self.csrf,
            author=self.author,
            title=self.title,
            chapters=[chapter.to_json() for chapter in self.chapters],
        )
        return json
