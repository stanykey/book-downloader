"""CLI for utility."""

from sys import exit

from litnet_downloader.book_downloader import BookDownloader


def run() -> None:
    url = 'https://litnet.com/ru/reader/para-dlya-drakona-ili-prosto-letim-domoi-b135045'
    token = 'look at cookies for value of <litera-frontend>'

    downloader = BookDownloader(url, token)

    book = downloader.get_book()
    with open(f'{book.title}.txt', 'w', encoding='utf-8') as file:
        for chapter in book.chapters:
            file.write(chapter.title)
            file.write('\n\n')

            content = chapter.content.replace('<p>', '\t')
            content = content.replace('</p>', '')
            file.write(content)

    input('Press Enter to continue...')


if __name__ == '__main__':
    exit(run())
