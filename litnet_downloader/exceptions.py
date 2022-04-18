"""This module contains the set of BookDownloader's exceptions."""


class DownloadException(Exception):
    def __init__(self, reason, **kwargs):
        self.reason = reason
        self.__dict__.update(kwargs)

    def __str__(self):
        return f"{self.reason}"
