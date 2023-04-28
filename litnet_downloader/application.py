"""CLI application."""
from enum import auto
from enum import StrEnum
from pathlib import Path
from re import fullmatch
from urllib.parse import urlparse

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


def book_index_url(url: str) -> str:
    """Returns well-formed book root URL or an empty string if impossible."""
    url_info = urlparse(url)

    if not all([url_info.scheme, url_info.netloc, url_info.path]):
        return ""

    if not fullmatch(pattern=r"\/([a-z]{2})\/reader\/([\w-]+)", string=url_info.path):
        return ""

    return f"{url_info.scheme}://{url_info.netloc}{url_info.path}"


def download_book(auth_token: str, book_url: str, book_format: BookFormat, working_dir: Path, use_cache: bool) -> None:
    if book_format is not BookFormat.txt:
        raise ValueError("unsupported format requested")

    try:
        downloader = DownloadManager(auth_token, working_dir)
        book = downloader.get_book(book_url, use_cache)

        exporter = BookExporter(working_dir=working_dir, formatter=TextFormatter())
        exporter.dump(book)
    except DownloadException as ex:
        echo(f"Error: {ex}", err=True, color=True)


@command()
@argument("url", type=str, help="book url to download")
@option(
    "-t",
    "--auth-token",
    type=str,
    required=True,
    help="the authentication token; could be obtained from cookie 'litera-frontend'",
)
@option(
    "-f",
    "--book-format",
    type=Choice(BookFormat),
    default=BookFormat.default,
    show_default=True,
    help="book save format",
)
@option(
    "-o",
    "--working-dir",
    type=Path,
    default=Path().absolute(),
    help="directory to download book  [default: current directory]",
)
@option(
    "-c",
    "--use-cache",
    type=bool,
    is_flag=True,
    default=True,
    show_default=True,
    help="don't delete temporary files; it might be useful if you decide to re-download a book in other formats)",
)
def cli(url: str, auth_token: str, book_format: BookFormat, working_dir: Path, use_cache: bool) -> None:
    """Small application for downloading books from litnet.com."""
    book_url = book_index_url(url)
    if not book_url:
        echo(f"url ({book_url}) isn't valid book url")
        return

    if book_format is not BookFormat.default:
        echo(f"selected format({book_format}) isn't supported yet. the `txt` format will be chosen")
        book_format = BookFormat.default

    download_book(auth_token, book_url, book_format, working_dir, use_cache)

    input("Press Enter to exit...")


if __name__ == "__main__":
    cli()
