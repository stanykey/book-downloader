"""CLI application.

auth-token could be obtained from cookie 'litera-frontend'

Usage:
    litnet-downloader interactive
    litnet-downloader <auth-token> <book-url> [--page-delay=<seconds>] [--certificate=<file>]
    litnet-downloader -h | --help | --version
"""


from pathlib import Path
from sys import exit
from time import sleep

from bs4 import BeautifulSoup
from docopt import docopt
from requests import RequestException

from litnet_downloader.book import Book
from litnet_downloader.book_downloader import BookDownloader
from litnet_downloader.exceptions import DownloadException
from litnet_downloader.utils import book_index_url
from litnet_downloader.version import __version__


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


def download_book(downloader: BookDownloader, book_url: str, use_cache: bool):
    try:
        book = get_book(downloader, book_url, use_cache)
        process_book(book)
    except DownloadException as ex:
        print(f'Error: {ex}')


def run_single_download(token: str, book_url: str, delay_secs: int, certificate: Path = None) -> None:
    downloader = BookDownloader(token, delay_secs, certificate)

    download_book(downloader, book_url, use_cache=True)

    answer = input('Delete cached books data? (yes/no): ')
    if answer.lower() == 'yes':
        downloader.reset_cache()

    input('Press Enter to exit...')


def run_interactive() -> None:
    token = input('enter auth token or press Enter to exit >> ')
    if not token:
        return

    certificate = input('[Optional] enter certificate path or press Enter to skip >>')
    certificate = Path(certificate).resolve() if certificate else None
    if certificate and not certificate.exists():
        print(f'warning: cert files ({certificate}) doesn\'t exist and will be skipped')
        certificate = None

    downloader = BookDownloader(token, certificate=certificate)
    while True:
        url = input('enter book url for download or press Enter to exit >> ')
        if not url:
            return

        if book_url := book_index_url(url):
            download_book(downloader, book_url, use_cache=True)
        else:
            print('invalid book url')
            print('valid form is https://litnet.com/<lang>/reader/<book-name>[?params...]')
            print()


def run() -> None:
    arguments = docopt(__doc__, version=__version__)
    if arguments.get('interactive'):
        return run_interactive()

    return run_single_download(
        token=arguments.get('<auth-token>'),
        book_url=arguments.get('<book-url>'),
        delay_secs=arguments['--page-delay'],
        certificate=arguments['--certificate']
    )


if __name__ == '__main__':
    exit(run())
