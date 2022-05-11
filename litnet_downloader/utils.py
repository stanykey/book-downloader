"""Utilities for different purposes."""
from re import fullmatch
from urllib.parse import urlparse


def is_book_url(url: str) -> bool:
    """Checks that <url> is corresponded to a book url schema."""
    result = urlparse(url)

    if not all([result.scheme, result.netloc, result.path]):
        return False

    return bool(fullmatch(pattern=r"\/([a-z]{2})\/reader\/([\w-]+)", string=result.path))


def book_index_url(url: str) -> str:
    """Returns well-formed book root URL or an empty string if impossible."""
    url_info = urlparse(url)

    if not all([url_info.scheme, url_info.netloc, url_info.path]):
        return ""

    if not fullmatch(pattern=r"\/([a-z]{2})\/reader\/([\w-]+)", string=url_info.path):
        return ""

    return f"{url_info.scheme}://{url_info.netloc}{url_info.path}"
