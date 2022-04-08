"""CLI application.

auth-token could be obtained from cookie 'litera-frontend'


Usage:
  litnet-downloader <auth-token> <book-url> [--page-delay=<seconds>]
  litnet-downloader -h | --help | --version
"""

from sys import exit
from time import sleep
from typing import Any

from bs4 import BeautifulSoup
from docopt import docopt
from requests import RequestException

from litnet_downloader.book import Book
from litnet_downloader.book_downloader import BookDownloader
from litnet_downloader.exceptions import DownloadException
from litnet_downloader.version import __version__


def get_option(options: dict[str, Any], key: str, /, *, default: Any = None) -> Any:
    option = options.get(key, default)
    return option if option else default


def get_book(downloader: BookDownloader, book_url: str, use_cache: bool) -> Book:
    while True:
        try:
            return downloader.get(book_url, use_cache, clean_after=False)
        except RequestException:
            pass
        sleep(5)  # TODO: maybe better is to pass as argument


def process_book(book: Book, /) -> None:
    with open(f'{book.title}.txt', 'w', encoding='utf-8') as book_file:
        for idx, chapter in enumerate(book.chapters):
            print(f'process {idx + 1} of {len(book.chapters)}')
            print(f'\ttitle: {chapter.title}')

            book_file.write(f'{chapter.title}\n\n')

            soup = BeautifulSoup(chapter.content)
            text_blocks = [block.get_text() for block in soup.find_all('p')]
            chapter_text = '\n\n'.join(text_blocks)

            print(f'\tchapter_text size: {len(chapter_text)}')

            book_file.write(chapter_text)
            book_file.write('\n\n\n\n')
            book_file.flush()


def run() -> None:
    arguments = docopt(__doc__, version=__version__)

    downloader = BookDownloader(
        token=arguments['<auth-token>'],
        delay_secs=int(get_option(arguments, '--page-delay', default=1))
    )

    book = get_book(downloader, book_url=arguments['<book-url>'], use_cache=True)
    process_book(book)

    answer = input('Delete cached books data? (yes/no) >> ')
    if answer.lower() == 'yes':
        downloader.reset_cache()

    input('Press Enter to exit...')


if __name__ == '__main__':
    try:
        exit(run())
    except DownloadException as ex:
        print(ex)
        exit(-1)
