"""This module contains setup instructions for litnet_downloader."""
from pathlib import Path

from setuptools import setup

from litnet_downloader.version import __version__


def read_requirements() -> list[str]:
    requirements_file = Path(__file__).parent.resolve() / "requirements.txt"
    with open(requirements_file, encoding="utf-8") as file:
        requirements = [line.strip() for line in file.readlines()]

    requirements.remove("setuptools")
    return requirements


setup(
    name="litnet_downloader",
    version=__version__,
    author_email="sergey.lovygin@yahoo.com",
    install_requires=read_requirements(),
    packages=["litnet_downloader"],
    entry_points={"console_scripts": ["litnet-downloader = litnet_downloader.cli:run"]},
    classifiers=[
        "Environment :: Console",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ],
    description="Python 3 package to download books from litnet.com.",
    python_requires=">=3.8",
)
