"""Literally, BookDownloader is the main class."""
from functools import cache
from hashlib import md5
from pathlib import Path
from shutil import rmtree
from time import sleep
from typing import Any
from typing import cast

from bs4 import BeautifulSoup
from requests import request as send_http_request
from requests import Response

from litnet_downloader.book_data import BookData
from litnet_downloader.book_data import ChapterData
from litnet_downloader.details.metadata import BookMetadata
from litnet_downloader.details.metadata import ChapterMetadata
from litnet_downloader.exceptions import DownloadException


class BookDownloader:
    @classmethod
    @cache
    def cache_location(cls) -> Path:
        return Path(__file__).parent.resolve() / ".cache"

    def __init__(self, token: str, delay_secs: int = 0, pem_path: Path | None = None):
        self._token = token
        self._delay = delay_secs
        self._pem_path = pem_path

        self._cookies = {"litera-frontend": token}

        self._cached_book_data: set[Path] = set()

    def get(self, book_url: str, /, use_cache: bool = True, clean_after: bool = True) -> BookData:
        book_dir = self._get_working_directory(book_url, clean=not use_cache)

        metadata = self._get_book_metadata(book_url, book_dir, use_cache)
        self._download_book_content(metadata, use_cache)

        book = self._make_book(metadata)

        if clean_after:
            self._remove_from_cache(book_dir)

        return book

    def reset_cache(self) -> None:
        for book_dir in list(self._cached_book_data):
            self._remove_from_cache(book_dir)

    def _get_book_metadata(self, url: str, working_dir: Path, use_cache: bool) -> BookMetadata:
        metadata = BookMetadata(working_dir)
        if use_cache and metadata.load() and metadata.completed:
            return metadata

        response = self._send_request(url)
        soup = BeautifulSoup(response.text, "lxml")
        try:
            # get common data
            metadata.csrf = soup.find("meta", attrs={"name": "csrf-token"}).attrs["content"]
            metadata.author = soup.find("a", class_="sa-name").text
            metadata.title = soup.find("h1", class_="book-heading").text

            # get chapters info
            metadata.chapters = self._load_chapters_metadata(soup, working_dir)
        except AttributeError:
            raise DownloadException(reason="Couldn't obtain metadata", response=response, url=url)

        if use_cache:
            metadata.save()

        return metadata

    @classmethod
    def _load_chapters_metadata(cls, soup: BeautifulSoup, working_dir: Path) -> list[ChapterMetadata]:
        try:
            chapters_list = soup.find("select", attrs={"name": "chapter"})
            chapters = [ChapterMetadata(item["value"], item.text) for item in chapters_list.find_all("option")]
        except AttributeError:
            # we have only one chapter so there is no correspond combo box
            node = soup.find("div", class_="reader-text")
            chapter_id = node["data-chapter"]
            chapter_title = node.find("h2").text
            chapters = [ChapterMetadata(chapter_id, chapter_title)]

        for meta in chapters:
            meta.content_path = cls.compose_chapter_path(meta, working_dir)

        return chapters

    def _download_book_content(self, meta: BookMetadata, use_cache: bool) -> None:
        for chapter in filter(lambda item: not (use_cache and item.downloaded), meta.chapters):
            self._download_chapter(chapter, meta)

    def _download_chapter(self, chapter: ChapterMetadata, meta: BookMetadata) -> None:
        print(f'download chapter "{chapter.title}"...')

        pages = self._get_chapter_content(chapter, meta)
        self._save_chapter_content(chapter, pages)

    def _get_chapter_content(self, chapter: ChapterMetadata, meta: BookMetadata) -> list[str]:
        data = self._download_page(chapter.id, 1, meta.csrf)

        pages = [data["data"]]
        for page_id in range(2, int(data["totalPages"]) + 1):
            response = self._download_page(chapter.id, page_id, meta.csrf)
            pages.append(response["data"])
        return pages

    @classmethod
    def _save_chapter_content(cls, chapter: ChapterMetadata, pages: list[str]) -> None:
        temp_location = chapter.content_path.with_suffix(".download")
        temp_location.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_location, "w", encoding="utf-8") as file:
            file.writelines(pages)
        temp_location.rename(chapter.content_path)

    @staticmethod
    def _make_book(meta: BookMetadata) -> BookData:
        book = BookData(
            author=meta.author,
            title=meta.title,
            chapters=[ChapterData(info.title, info.load_content()) for info in meta.chapters],
        )
        return book

    def _get_working_directory(self, book_url: str, clean: bool) -> Path:
        book_path = self.compose_book_path(book_url)
        if book_path.exists() and clean:
            self._remove_directory(book_path)

        self._add_to_cache(book_path)

        return book_path

    def _send_request(self, url: str, **kwargs: Any) -> Response:
        return send_http_request("GET", url, cookies=self._cookies, verify=self._pem_path, **kwargs)

    def _download_page(self, chapter_id: str, page_index: int, csrf: str) -> dict[str, Any]:
        sleep(self._delay)  # TODO: find better approach

        response = self._send_request(
            url="https://litnet.com/reader/get-page",
            headers={"X-CSRF-Token": csrf},
            data={"chapterId": chapter_id, "page": page_index},
        )

        return cast(dict[str, Any], response.json())

    def _add_to_cache(self, book_dir: Path) -> None:
        if book_dir in self._cached_book_data:
            return

        book_dir.mkdir(exist_ok=True, parents=True)
        self._cached_book_data.add(book_dir)

    def _remove_from_cache(self, book_dir: Path) -> None:
        if book_dir not in self._cached_book_data:
            return

        self._remove_directory(book_dir)
        self._cached_book_data.remove(book_dir)

    @staticmethod
    def _get_hash(data: str) -> str:
        return md5(data.encode("utf-8")).hexdigest()

    @staticmethod
    def _remove_directory(dir_path: Path) -> None:
        rmtree(dir_path, ignore_errors=True)

    @classmethod
    def compose_book_path(cls, book_url: str) -> Path:
        book_dir_name = cls._get_hash(book_url)
        return cls.cache_location() / book_dir_name

    @classmethod
    def compose_chapter_path(cls, chapter: ChapterMetadata, book_dir: Path) -> Path:
        file_name = cls._get_hash(f"[{chapter.id}][{chapter.title}]")
        return book_dir / "chapters" / file_name
