"""This module contains setup instructions for litnet_downloader."""

from setuptools import setup

from litnet_downloader.version import __version__


setup(
    name='litnet_downloader',
    version=__version__,
    author_email='sergey.lovygin@yahoo.com',
    packages=['litnet_downloader'],
    entry_points={
        'console_scripts': [
            'litnet-downloader = litnet_downloader.cli:run'
        ]
    },
    classifiers=[
        'Environment :: Console',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    description='Python 3 package to download books from litnet.com.',
    python_requires='>=3.8'
)
