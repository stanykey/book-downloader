"""Small core helpers."""
from re import fullmatch
from urllib.parse import urlparse

from aiohttp import ClientError
from aiohttp import ClientSession
from aiohttp import ClientTimeout


def canonical_book_url(url: str) -> str:
    """Return well-formed book root URL or an empty string if impossible."""
    url_info = urlparse(url)

    if not all([url_info.scheme, url_info.netloc, url_info.path]):
        return ""

    if not fullmatch(pattern=r"\/([a-z]{2})\/reader\/([\w-]+)", string=url_info.path):
        return ""

    return f"{url_info.scheme}://{url_info.netloc}{url_info.path}"


async def is_url_accessible(url: str) -> bool:
    """
    Check availability of the `url`.

    Not the best way, but better then nothing
    """
    try:
        timeout = ClientTimeout(total=5)  # 5secs for all
        async with ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return True
    except (TimeoutError, ClientError):
        return False
