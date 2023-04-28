# litnet-book-downloader

Small application for downloading books from litnet.com


---
## General notes
It's an educational project with some personal profit: it allows you to download books for reading for cases when you don't have an Internet connection.

The initial education points were the following:
- web scraping
- better understanding of how websites work
  - logins
  - cookies
  - some security moments
- asyncio
- ebook composing

---
## Task List
- [x] add a possibility to continue/recover work after a crash or any other reason
- [x] turn all implicit settings to explicit if make sense
- [x] segregate components into the core, internal, and the app
- [ ] make everything async
- [ ] save a book into selected format
  - [x] txt
  - [ ] epub
  - [ ] fb2
- [ ] login into the site via any available source
  - [ ] pickup cookies for further use
- [ ] improve ways to circumvent downloads protection mechanisms


---
### For contributors

If you want to contribute, please do the following:
- ensure you have installed the pre-commit package
- run the `pre-commit install` command
- [optional] run the `pre-commit run --all-files` command
