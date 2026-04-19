# Project Overview

## What this project does

`book-downloader` is a CLI utility that downloads books from Litnet and exports them as plain text files.
Today, only Litnet and `txt` are implemented.

## Stack

- Python `>=3.14`
- Async I/O: `asyncio`, `aiohttp`, `aiofiles`
- Parsing: `beautifulsoup4`, `lxml`
- CLI: `click`

## Entry Point

- Console script: `book-downloader`
- Module entry: `book_downloader.application:cli`

Example usage pattern:

```bash
book-downloader "<reader-url>" --auth-token "<litera-frontend-cookie-value>"
```

## High-Level Architecture

The code is split into three layers:

- `application.py`: CLI, argument handling, orchestration.
- `core/`: domain flow (download manager, book model, export).
- `internal/`: implementation details (network helpers, metadata persistence, Litnet downloader internals).
- `sites/`: service adapters and service factory (`LitnetService` today).

## Download Flow

1. CLI resolves service by URL (`litnet.com` -> `ServiceId.Litnet`).
2. URL is normalized to a canonical Litnet reader URL.
3. Reachability check runs for the book URL.
4. `DownloadManager` chooses a working directory:
   - cache directory (`<working_dir>/.downloads-cache/<book-hash>`) if `--use-cache`
   - temp directory if cache is disabled
5. `LitnetBookDownloader`:
   - downloads index page
   - extracts CSRF token, author, title, chapter list
   - stores metadata in `metadata.json`
   - downloads chapter pages from `https://litnet.com/reader/get-page`
   - saves each chapter as hashed file under `chapters/`
6. `DownloadManager` builds `BookData` from metadata and chapter files.
7. `BookExporter` writes final output with `TextFormatter` to:
   - `"[{author}]{title}.txt"` in selected working directory.

## Data and Caching Model

- Per-book folder key is SHA-256 of book URL.
- Chapter file names are SHA-256 of `[chapter-id][chapter-title]`.
- Metadata is persisted to `metadata.json` for resume/recovery.
- Existing chapter files are treated as already downloaded.

## Core Components

- `DownloadManager`: lifecycle and cache/temp directory strategy.
- `BookMetadata` / `ChapterMetadata`: persisted state + chapter content loading.
- `LitnetBookDownloader`: Litnet-specific scraping/downloading logic.
- `TextFormatter` + `BookExporter`: conversion from chapter HTML to final text file.

## Current Constraints / Gaps

- Only Litnet is supported.
- Only `txt` export is implemented (`epub` and `fb2` are placeholders).
- CLI requires `--auth-token`; login-agent flow exists but is not integrated into CLI.
- Book URL validation accepts only `/xx/reader/<slug>` style paths.
- Some operations remain synchronous (`ping`, parsing, some filesystem calls).

## Where to extend

- Add new providers in `sites/` + corresponding downloader in `internal/downloaders/`.
- Add more formatters in `core/formatters/` and wire them in `application.py`.
- Integrate `internal/login_agent.py` into CLI for interactive token acquisition.
- Move CPU-bound parsing/serialization to thread pool (`internal/asyncio.py` already exists).
