# litnet-book-downloader

Small application for downloading books from litnet.com

---
Actually, this is an educational project with some personal profit: allows you to download books to read when you don't have an Internet connection
- web scraping
- better understanding of how websites work
  - logins
  - cookies
  - some security moments
- upload to Google disk
- ebook composing

---
# Task List
- [x] add a possibility to continue/recover work after a crash or any other reason
- [ ] login into the site via any available source
  - [ ] pickup cookies for further use
- [ ] upload to Google disk
- [ ] compose result output file
  - [x] txt
  - [ ] epub
  - [ ] fb2
- [ ] improve ways to circumvent downloads protection mechanisms
- [ ] improve UI (make fancy command-line UI)


---
For contributors

If you want to contribute please do the following:
- ensure you have installed the pre-commit package
- run `pre-commit install`
- [optionaly] run `pre-commit run --all-files`
