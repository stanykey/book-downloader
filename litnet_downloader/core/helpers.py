"""Small core helpers."""
from re import fullmatch
from urllib.parse import urlparse


def canonical_book_url(url: str) -> str:
    """Returns well-formed book root URL or an empty string if impossible."""
    url_info = urlparse(url)

    if not all([url_info.scheme, url_info.netloc, url_info.path]):
        return ""

    if not fullmatch(pattern=r"\/([a-z]{2})\/reader\/([\w-]+)", string=url_info.path):
        return ""

    return f"{url_info.scheme}://{url_info.netloc}{url_info.path}"
