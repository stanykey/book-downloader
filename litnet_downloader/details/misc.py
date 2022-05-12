"""Holds small and handy miscellaneous."""
from hashlib import md5
from pathlib import Path
from shutil import rmtree


def fingerprint(data: str) -> str:
    return md5(data.encode("utf-8")).hexdigest()


def remove_directory(dir_path: Path) -> None:
    rmtree(dir_path, ignore_errors=True)
