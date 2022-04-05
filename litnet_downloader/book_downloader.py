"""Literally, BookDownloader is the main class."""

from copy import deepcopy
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

    def download_content(self) -> None:
        for idx, chapter in enumerate(self._chapters):
            print(f'{idx}/{len(self._chapters)} download "{chapter.title}"...')

            data = self._download_page(chapter.id, 1)
            chapter.title = data['chapterTitle']

            pages = [data['data']]
            for page_id in range(2, int(data['totalPages']) + 1):
                pages += self._download_page(chapter.id, page_id)['data']
            chapter.content = ''.join(pages)

    def get_book(self) -> Book:
        if not self._book:
            self.download_content()
            self._book = Book(self._author, self._title, self._chapters)
        return deepcopy(self._book)

    def __repr__(self):
        return f'BookDownloader(url: {self._url}, token: {self._token}, delay: {self._delay})'

    def _load_book_metadata(self):
        response = requests.request('GET', url=self._url, cookies=self._cookies, verify=False)

        soup = BeautifulSoup(response.text, 'lxml')
        try:
            self._csrf = soup.find('meta', attrs={'name': 'csrf-token'}).attrs['content']
            self._author = soup.find('a', class_='sa-name').text
            self._title = soup.find('h1', class_='book-heading').text

            try:
                chapters_list = soup.find('select', attrs={'name': 'chapter'})
                self._chapters = [
                    Chapter(item['value'], item.text)
                    for item in chapters_list.find_all('option')
                ]
            except AttributeError:
                # we have only one chapter
                node = soup.find('div', class_='reader-text')
                chapter_id = node['data-chapter']
                chapter_title = node.find('h2').text
                self._chapters = [Chapter(chapter_id, chapter_title)]

        except AttributeError:
            print('Metadata read is failed!')

    def _download_page(self, chapter_id: str, page_index: int):
        sleep(self._delay)

        response = requests.request(
            'get',
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
