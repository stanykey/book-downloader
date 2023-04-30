from re import fullmatch
from urllib.parse import urlparse

from book_downloader.internal.downloaders import LitnetBookDownloader
from book_downloader.internal.network import is_url_reachable
from book_downloader.internal.network import ping


class LitnetService:
    """Implement the `Service` protocol."""

    def __init__(self, token: str) -> None:
        self._token = token

    @classmethod
    def host(cls) -> str:
        return "litnet.com"

    @classmethod
    async def check_service(cls) -> bool:
        return ping(cls.host())

    @classmethod
    async def check_url(cls, url: str) -> bool:
        return await is_url_reachable(url)

    @classmethod
    def canonical_book_url(cls, url: str) -> str:
        """Return well-formed book root URL or an empty string if impossible."""
        url_info = urlparse(url)

        if not all([url_info.scheme, url_info.netloc, url_info.path]):
            return ""

        if not fullmatch(pattern=r"\/([a-z]{2})\/reader\/([\w-]+)", string=url_info.path):
            return ""

        return f"{url_info.scheme}://{url_info.netloc}{url_info.path}"

    def get_downloader(self) -> LitnetBookDownloader:
        return LitnetBookDownloader(self._token)
