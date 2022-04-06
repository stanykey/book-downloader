"""Literally, BookDownloader is the main class."""

from hashlib import md5
from pathlib import Path
from shutil import rmtree
from time import sleep

import requests
from bs4 import BeautifulSoup

from litnet_downloader.book import Book, Chapter


class BookDownloader:
    def __init__(self, *, url: str, token: str, delay_secs: int = 1):
        self._url = url
        self._token = token
        self._delay = delay_secs

        self._cookies = {
            'litera-frontend': token
        }

        self._csrf = ''
        self._author = ''
        self._title = ''
        self._chapters: list[Chapter] = []
        self._load_book_metadata()

        self._book = None

    def download_content(self) -> bool:
        for chapter in filter(lambda item: not item.downloaded, self._chapters):
            print(f'download chapter "{chapter.title}"...')

            try:
                data = self._download_page(chapter.id, 1)

                pages = [data['data']]
                for page_id in range(2, int(data['totalPages']) + 1):
                    response = self._download_page(chapter.id, page_id)
                    pages.append(response['data'])

                with open(chapter.location, 'w', encoding='utf-8') as file:
                    content = ''.join(pages)
                    file.write(content)
            except:
                # we got some error (maybe we were blocked server)
                return False

        # all chapters were downloaded
        return True

    def get_book(self) -> Book:
        if not self._book and self.download_content():
            self._book = Book(self._author, self._title, self._chapters)
        return self._book

    def cleanup(self) -> None:
        rmtree(self._working_dir, ignore_errors=True)

    def __repr__(self):
        return f'BookDownloader(url: {self._url}, token: {self._token}, delay: {self._delay})'

    def _load_book_metadata(self) -> None:
        response = requests.request('GET', url=self._url, cookies=self._cookies, verify=False)

        soup = BeautifulSoup(response.text, 'lxml')
        try:
            self._load_general_metadata(soup)
            self._load_chapters_metadata(soup)

        except AttributeError:
            print('Metadata read is failed!')

    def _get_working_directory(self) -> None:
        cache_location = Path(__file__).parent.resolve() / '.cache'
        book_dir_name = self._get_hash(f'[book][{self._author}][{self._title}]')
        self._working_dir = cache_location / book_dir_name

        self._working_dir.mkdir(exist_ok=True, parents=True)

    def _load_general_metadata(self, soup: BeautifulSoup) -> None:
        self._csrf = soup.find('meta', attrs={'name': 'csrf-token'}).attrs['content']
        self._author = soup.find('a', class_='sa-name').text
        self._title = soup.find('h1', class_='book-heading').text
        self._get_working_directory()

    def _load_chapters_metadata(self, soup: BeautifulSoup) -> None:
        try:
            chapters_list = soup.find('select', attrs={'name': 'chapter'})
            self._chapters = [
                Chapter(item['value'], item.text, self._get_chapter_path(item['value'], item.text))
                for item in chapters_list.find_all('option')
            ]
        except AttributeError:
            # we have only one chapter so there is no correspond combo box
            node = soup.find('div', class_='reader-text')
            chapter_id = node['data-chapter']
            chapter_title = node.find('h2').text
            self._chapters = [Chapter(chapter_id, chapter_title, self._get_chapter_path(chapter_id, chapter_title))]

    def _get_chapter_path(self, chapter_id: str, chapter_title: str) -> Path:
        file_name = self._get_hash(f'[chapter][{chapter_id}][{chapter_title}]')
        return self._working_dir / file_name

    def _download_page(self, chapter_id: str, page_index: int):
        sleep(self._delay)  # TODO: find better approach

        response = requests.request(
            'GET',
            url='https://litnet.com/reader/get-page',
            cookies=self._cookies,
            verify=False,
            headers={
                'X-CSRF-Token': self._csrf
            },
            data={
                'chapterId': chapter_id,
                'page': page_index
            }
        )

        return response.json()

    @staticmethod
    def _get_hash(data: str) -> str:
        return md5(data.encode('utf-8')).hexdigest()
