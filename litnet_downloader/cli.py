"""CLI application.

auth-token could be obtained from cookie 'litera-frontend'

Usage:
    litnet-downloader interactive
    litnet-downloader <auth-token> <book-url> [--page-delay=<seconds>] [--certificate=<file>]
    litnet-downloader -h | --help | --version
"""
from pathlib import Path

from docopt import docopt

from litnet_downloader.book_data import BookData
from litnet_downloader.book_downloader import BookDownloader
from litnet_downloader.book_exporter import BookExporter
from litnet_downloader.exceptions import DownloadException
from litnet_downloader.formatters import TextFormatter
from litnet_downloader.utils import book_index_url


def download_book_data(downloader: BookDownloader, book_url: str, use_cache: bool) -> BookData:
    return downloader.get(book_url, use_cache, clean_after=False)


def export_book_data(book: BookData, /) -> None:
    exporter = BookExporter(output_root=Path(__file__).parent / "books", exporter=TextFormatter())
    exporter.dump(book)


def download_book(downloader: BookDownloader, book_url: str, use_cache: bool) -> None:
    try:
        book_data = download_book_data(downloader, book_url, use_cache)
        export_book_data(book_data)
    except DownloadException as ex:
        print(f"Error: {ex}")


def run_single_download(token: str, book_url: str, delay_secs: int, pem_path: Path | None = None) -> None:
    downloader = BookDownloader(token, delay_secs, pem_path)

    download_book(downloader, book_url, use_cache=True)

    answer = input("Delete cached books data? (yes/no): ")
    if answer.lower() == "yes":
        downloader.reset_cache()

    input("Press Enter to exit...")


def run_interactive() -> None:
    token = input("enter auth token or press Enter to exit >> ")
    if not token:
        return

    pem_path = Path(input("[Optional] enter certificate path or press Enter to skip >>")).resolve()
    is_pem_path_valid = pem_path.exists() and pem_path.is_file()
    if not is_pem_path_valid:
        print(f"warning: cert files ({pem_path}) doesn't exist and will be skipped")

    downloader = BookDownloader(token, pem_path=pem_path if is_pem_path_valid else None)
    while True:
        url = input("enter book url for download or press Enter to exit >> ")
        if not url:
            return

        if book_url := book_index_url(url):
            download_book(downloader, book_url, use_cache=True)
        else:
            print("invalid book url")
            print("valid form is https://litnet.com/<lang>/reader/<book-name>[?params...]")
            print()


def main() -> None:
    """Application entry point."""
    arguments = docopt(__doc__)
    if arguments.get("interactive"):
        return run_interactive()

    return run_single_download(
        token=arguments.get("<auth-token>"),
        book_url=arguments.get("<book-url>"),
        delay_secs=arguments["--page-delay"],
        pem_path=arguments["--certificate"],
    )


if __name__ == "__main__":
    main()
