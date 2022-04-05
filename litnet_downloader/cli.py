"""CLI application.

auth-token could be obtained from cookie 'litera-frontend'


Usage:
  litnet-downloader <auth-token> <book-url> [--page-delay=<seconds>]
  litnet-downloader -h | --help | --version
"""

from sys import exit
from typing import Any

from docopt import docopt

from litnet_downloader.book_downloader import BookDownloader
from litnet_downloader.version import __version__


def get_option(options: dict[str, Any], key: str, /, *, default: Any = None) -> Any:
    option = options.get(key, default)
    return option if option else default


def run() -> None:
    arguments = docopt(__doc__, version=__version__)

    downloader = BookDownloader(
        url=arguments['<book-url>'],
        token=arguments['<auth-token>'],
        delay_secs=get_option(arguments, '--page-delay', default=1)
    )

    book = downloader.get_book()
    with open(f'{book.title}.txt', 'w', encoding='utf-8') as file:
        for chapter in book.chapters:
            file.write(chapter.title)
            file.write('\n\n')

            content = chapter.content.replace('<p>', '\t')
            content = content.replace('</p>', '')
            file.write(content)

    input('Press Enter to continue...')


if __name__ == '__main__':
    exit(run())
