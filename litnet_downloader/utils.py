"""Utilities for different purposes."""

from re import fullmatch
from urllib.parse import urlparse


def is_book_url(url: str) -> bool:
    result = urlparse(url)

    if not all([result.scheme, result.netloc, result.path]):
        return False

    return bool(fullmatch(
        pattern=r'\/([a-z]{2})\/reader\/([\w-]+)',
        string=result.path
    ))


def book_index_url(url: str) -> str:
    url = urlparse(url)

    if not all([url.scheme, url.netloc, url.path]):
        return ''

    if not fullmatch(pattern=r'\/([a-z]{2})\/reader\/([\w-]+)', string=url.path):
        return ''

    return f'{url.scheme}://{url.netloc}{url.path}'
