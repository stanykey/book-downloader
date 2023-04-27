"""CLI application."""
from enum import auto
from enum import StrEnum
from pathlib import Path

from click import argument
from click import Choice
from click import command
from click import echo
from click import option

from litnet_downloader.book_exporter import BookExporter
from litnet_downloader.download_manager import DownloadManager
from litnet_downloader.exceptions import DownloadException
from litnet_downloader.formatters import TextFormatter


class BookFormat(StrEnum):
    txt = auto()
    epub = auto()
    fb2 = auto()
    default = txt


def download_book(downloader: DownloadManager, book_url: str, book_format: BookFormat, use_cache: bool) -> None:
    if book_format is not BookFormat.txt:
        raise ValueError("unsupported format requested")

    try:
        book = downloader.get_book(book_url, use_cache, clean_after=False)

        exporter = BookExporter(output_root=Path(__file__).parent / "books", exporter=TextFormatter())
        exporter.dump(book)
    except DownloadException as ex:
        echo(f"Error: {ex}", err=True, color=True)


@command()
@argument("book-url", type=str, default="test-debug-value")
@option(
    "--auth-token",
    type=str,
    required=True,
    help="the authentication token; could be obtained from cookie 'litera-frontend'",
)
@option(
    "--book-format",
    type=Choice(BookFormat),
    default=BookFormat.default,
    show_default=True,
    help="book save format",
)
@option(
    "--use-cache",
    type=bool,
    is_flag=True,
    default=True,
    show_default=True,
    help="don't delete temporary files; it might be useful if you decide to re-download a book in other formats)",
)
def cli(book_url: str, auth_token: str, book_format: BookFormat, use_cache: bool) -> None:
    """Small application for downloading books from litnet.com."""
    if book_format is not BookFormat.default:
        echo(f"selected format({book_format}) isn't supported yet. the `txt` format will be chosen")
        book_format = BookFormat.default

    downloader = DownloadManager(auth_token)

    download_book(downloader, book_url, book_format, use_cache)

    input("Press Enter to exit...")


if __name__ == "__main__":
    cli()
