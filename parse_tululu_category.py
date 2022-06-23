#!/usr/bin/python
"""
Скрипт для скачивания книг из библиотеки tululu.org
"""
import json

from urllib.parse import urljoin, urlsplit, unquote

import requests
from bs4 import BeautifulSoup

from parse_tululu import parse_book_page, download_txt,  download_image


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def parse_category_pages(url_category, page_count):
    book_pages = []
    for number_page in range(1, page_count+1):
        if number_page > 1:
            url_page = f'{url_category}/{number_page}'
        else:
            url_page = url_category
        params = ''
        response = requests.get(url_page, params=params)
        response.raise_for_status()
        check_for_redirect(response)

        soup = BeautifulSoup(response.text, 'lxml')
        book_items_selector = ".d_book tr:nth-child(2) td a"
        book_items = soup.select(book_items_selector)
        print(book_items)
        for book_item in book_items:
            book_page = urljoin(url_page, book_item['href'])
            print(book_page)
            book_pages.append(book_page)
    return book_pages


def main():

    book_folder = 'books'
    url_txt = 'https://tululu.org/txt.php'
    url_scifi_cat = 'https://tululu.org/l55/'

    print(f'Программа начинает скачивание книг SciFi по 4 страницу')
    book_pages = parse_category_pages(url_scifi_cat, 4)
    print(book_pages)
    books_properties = []
    for book_page in book_pages:

        book_properties = None
        id_book = urlsplit(unquote(book_page)).path.strip('/')[1:]
        try:
            response = requests.get(book_page)
            response.raise_for_status()
            check_for_redirect(response)
            book_properties = parse_book_page(
                response.text,
                book_page
            )
            filename = f'{id_book}. {book_properties["title"]}.txt'
            params = {'id': id_book, }
            download_txt(url_txt, filename, book_folder, params)
            download_image(book_properties['img_path'])

            print(f'Заголовок: {book_properties["title"]}')
            print(f'Автор: {book_properties["author"]}')
            print(f'Жанры: {book_properties["genres"]}')
            print(f'{len(book_properties["comments"])} комментарий/я/ев: ')
            for i, comment in enumerate(book_properties["comments"]):
                print(f'{i + 1}. {comment}')
            print()

        except requests.HTTPError:
            print(f'На сайте нет книги {id_book} ', end='')
            if book_properties:
                print(book_properties['title'])
            print(end='\n')
        books_properties.append(book_properties)

    with open('books_scifi.json', 'w''', encoding='utf8') as my_file:
        json.dump(books_properties, my_file, ensure_ascii=False)


if __name__ == '__main__':
    main()
