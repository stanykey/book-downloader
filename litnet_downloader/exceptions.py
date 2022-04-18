"""This module contains the set of BookDownloader's exceptions."""
from typing import Any


class DownloadException(Exception):
    def __init__(self, reason: str, **kwargs: Any):
        self.reason = reason
        self.__dict__.update(kwargs)

    def __str__(self) -> str:
        return f"{self.reason}"
