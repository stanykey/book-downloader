"""Performs async downloading of book metadata."""

from asyncio import gather as wait_for_all
from asyncio import sleep as sleep_for
from json import JSONDecodeError
from pathlib import Path
from random import randint
from typing import Any
from typing import cast

from aiofiles import open as open_file
from aiohttp import ClientResponseError
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from bs4.element import Tag

from book_downloader.core.exceptions import DownloadException
from book_downloader.internal.metadata import BookMetadata
from book_downloader.internal.metadata import ChapterMetadata
from book_downloader.internal.misc import fingerprint


class LitnetBookDownloader:
    def __init__(self, token: str):
        self._token = token
        self._cookies = {"litera-frontend": token}

    async def download(self, book_url: str, book_dir: Path) -> BookMetadata:
        return await self._download_book(book_url, book_dir)

    async def _download_book(self, book_url: str, book_dir: Path) -> BookMetadata:
        metadata = await self._get_book_metadata(book_url, book_dir)
        await self._download_book_content(metadata)
        return metadata

    async def _get_book_metadata(self, url: str, working_dir: Path) -> BookMetadata:
        metadata = BookMetadata(working_dir)
        if await metadata.load() and metadata.completed:
            return metadata

        response = await self._get_book_index_page(url)
        soup = BeautifulSoup(response, "lxml")
        try:
            # get common data
            csrf_meta = soup.find("meta", attrs={"name": "csrf-token"})
            if not isinstance(csrf_meta, Tag):
                raise AttributeError("csrf meta tag not found")
            csrf = csrf_meta.get("content")
            if not isinstance(csrf, str):
                raise AttributeError("csrf content is missing")
            metadata.csrf = csrf

            author_node = soup.find("a", class_="sa-name")
            if not isinstance(author_node, Tag):
                raise AttributeError("author node not found")
            metadata.author = author_node.get_text()

            title_node = soup.find("h1", class_="book-heading")
            if not isinstance(title_node, Tag):
                raise AttributeError("title node not found")
            metadata.title = title_node.get_text()

            # get chapters info
            metadata.chapters = await self._load_chapters_metadata(soup, working_dir)
        except AttributeError as ex:
            raise DownloadException(reason="Couldn't obtain metadata", response=response, url=url) from ex

        await metadata.save()

        return metadata

    @classmethod
    async def _load_chapters_metadata(cls, soup: BeautifulSoup, working_dir: Path) -> list[ChapterMetadata]:
        try:
            chapters_list = soup.find("select", attrs={"name": "chapter"})
            if not isinstance(chapters_list, Tag):
                raise AttributeError("chapters list node not found")

            chapters: list[ChapterMetadata] = []
            for item in chapters_list.find_all("option"):
                if not isinstance(item, Tag):
                    continue
                chapter_id = item.get("value")
                if not isinstance(chapter_id, str):
                    continue
                chapters.append(ChapterMetadata(chapter_id, item.get_text()))

            if not chapters:
                raise AttributeError("chapter options are missing")
        except AttributeError as ex:
            # we have only one chapter so there is no correspond combo box
            node = soup.find("div", class_="reader-text")
            if not isinstance(node, Tag):
                raise AttributeError("reader text node not found") from ex

            chapter_id = node.get("data-chapter")
            if not isinstance(chapter_id, str):
                raise AttributeError("chapter id is missing") from ex

            chapter_title_node = node.find("h2")
            if not isinstance(chapter_title_node, Tag):
                raise AttributeError("chapter title node not found") from ex
            chapter_title = chapter_title_node.get_text()
            chapters = [ChapterMetadata(chapter_id, chapter_title)]

        for meta in chapters:
            meta.content_path = cls._compose_chapter_path(meta, working_dir)

        return chapters

    async def _download_book_content(self, meta: BookMetadata) -> None:
        headers = {"X-CSRF-Token": meta.csrf}
        async with ClientSession(headers=headers, cookies=self._cookies) as session:
            chapters = list(filter(lambda item: not item.downloaded, meta.chapters))
            tasks = (self._download_chapter(session, chapter) for chapter in chapters)
            await wait_for_all(*tasks)

    async def _download_chapter(self, session: ClientSession, chapter: ChapterMetadata) -> None:
        pages = await self._get_chapter_content(session, chapter)
        await self._save_chapter_content(chapter, pages)

    async def _get_chapter_content(self, session: ClientSession, chapter: ChapterMetadata) -> list[str]:
        data = await self._get_chapter_data(session, chapter.id, 1)
        if "data" not in data:
            return []

        pages = [data["data"]]
        for page_id in range(2, int(data["totalPages"]) + 1):
            response = await self._get_chapter_data(session, chapter.id, page_id)
            if "data" not in response:
                return []
            pages.append(response["data"])

        print(f"chapter {chapter.title} is downloaded")
        return pages

    @classmethod
    async def _save_chapter_content(cls, chapter: ChapterMetadata, pages: list[str]) -> None:
        if not pages:
            return

        temp_location = chapter.content_path.with_suffix(".download")
        temp_location.parent.mkdir(parents=True, exist_ok=True)
        async with open_file(temp_location, "w", encoding="utf-8") as file:
            await file.writelines(pages)
        temp_location.rename(chapter.content_path)

    async def _get_book_index_page(self, url: str) -> str:
        async with ClientSession(cookies=self._cookies) as session:
            async with session.get(url) as response:
                return await response.text()

    @staticmethod
    async def _get_chapter_data(session: ClientSession, chapter_id: str, page: int) -> dict[str, Any]:
        url = "https://litnet.com/reader/get-page"
        data = {"chapterId": chapter_id, "page": page}

        wait_duration = randint(0, 2)
        await sleep_for(wait_duration)
        async with session.get(url, data=data) as response:
            try:
                page_data = await response.json(content_type="text/html; charset=utf-8")
                return cast(dict[str, Any], page_data)
            except ClientResponseError:
                return dict()
            except JSONDecodeError:
                return dict()

    @classmethod
    def _compose_chapter_path(cls, chapter: ChapterMetadata, book_dir: Path) -> Path:
        file_name = fingerprint(f"[{chapter.id}][{chapter.title}]")
        return book_dir / "chapters" / file_name
