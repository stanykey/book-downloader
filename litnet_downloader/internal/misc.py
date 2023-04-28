"""Holds small and handy miscellaneous."""
from hashlib import sha256
from pathlib import Path
from shutil import rmtree


def fingerprint(data: str) -> str:
    """Returns some kind of hash."""
    return sha256(data.encode("utf-8")).hexdigest()


def ensure_directory_exists(path: Path) -> None:
    """Creates a new directory at this given path if not existing."""
    path.mkdir(exist_ok=True, parents=True)


def remove_directory(path: Path) -> None:
    """Recursively deletes a directory tree (ignores any errors)."""
    rmtree(path, ignore_errors=True)
