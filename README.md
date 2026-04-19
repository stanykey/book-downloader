# book-downloader

CLI utility for downloading books from Litnet and exporting them as text files.

## Quick Start

1. Install dependencies:

```bash
uv sync
```

2. Run:

```bash
uv run book-downloader "<book-reader-url>" --auth-token "<litera-frontend-cookie-value>"
```

## Documentation

- [Docs Index](docs/README.md)
- [Project Overview](docs/project-overview.md)
- [CLI Reference](docs/cli.md)
- [Roadmap](docs/roadmap.md)

## Current Scope

- Supported site: `litnet.com`
- Supported export format: `txt`
