"""CLI application."""
from asyncio import run
from pathlib import Path

from click import argument
from click import Choice
from click import command
from click import echo
from click import option

from book_downloader.core.book_exporter import BookExporter
from book_downloader.core.download_manager import DownloadManager
from book_downloader.core.exceptions import DownloadException
from book_downloader.core.formatters import BookFormat
from book_downloader.core.formatters import TextFormatter
from book_downloader.sites import make_service
from book_downloader.sites import Service
from book_downloader.sites import ServiceId


def get_service_id(url: str) -> ServiceId | None:
    if "litnet.com" in url:
        return ServiceId.Litnet

    return None


async def download_book(
    service: Service, book_url: str, save_format: BookFormat, working_dir: Path, use_cache: bool
) -> None:
    if save_format is not BookFormat.txt:
        raise ValueError("unsupported format requested")

    try:
        download_manager = DownloadManager(working_dir)
        downloader = service.get_downloader()
        book = await download_manager.get_book(book_url, downloader, use_cache)

        exporter = BookExporter(working_dir=working_dir, formatter=TextFormatter())
        await exporter.dump(book)
    except DownloadException as ex:
        echo(f"Error: {ex}", err=True, color=True)


@command()
@argument("url", type=str)
@option(
    "-t",
    "--auth-token",
    type=str,
    required=True,
    help="the authentication token; could be obtained from cookie 'litera-frontend'",
)
@option(
    "-f",
    "--save-format",
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
def cli(url: str, auth_token: str, save_format: BookFormat, working_dir: Path, use_cache: bool) -> None:
    """Small application for downloading books from litnet.com."""
    service_id = get_service_id(url)
    if not service_id:
        echo(f"can't determine service for url ({url})", err=True)
        return

    service = make_service(service_id, auth_token)
    if not service:
        echo(f"service {service_id!r} isn't implemented yet", err=True)
        return

    url = service.canonical_book_url(url)
    if not url:
        echo(f"url ({url}) isn't valid book url", err=True)
        return

    if not run(service.check_url(url)):
        echo(f"url ({url}) is unreachable", err=True)
        return

    if save_format is not BookFormat.default:
        echo(f"selected format({save_format}) isn't supported yet. the `txt` format will be chosen", err=True)
        save_format = BookFormat.default

    run(download_book(service, url, save_format, working_dir, use_cache))

    input("Press Enter to exit...")


if __name__ == "__main__":
    cli()
