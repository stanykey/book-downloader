# CLI Reference

## Entry Point

- Script: `book-downloader`
- Module: `book_downloader.application:cli`

## Command

```bash
book-downloader URL --auth-token TOKEN [options]
```

## Arguments

- `URL` (required): Litnet book reader URL in format like `/xx/reader/<slug>`.

## Options

- `-t, --auth-token` (required): value of cookie `litera-frontend`.
- `-f, --save-format` (default: `txt`): currently only `txt` is effectively supported.
- `-o, --working-dir` (default: current directory): output and cache base directory.
- `-c, --use-cache` (flag, default: enabled): keep temporary downloaded data for reuse.

## Example

```bash
uv run book-downloader "https://litnet.com/en/reader/book-slug" --auth-token "your-token"
```

## Notes

- The command validates URL and checks reachability before download.
- Unsupported format choices are currently forced back to `txt`.
