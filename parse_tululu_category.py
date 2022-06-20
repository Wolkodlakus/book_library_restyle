#!/usr/bin/python
"""
Скрипт для скачивания книг из библиотеки tululu.org
"""
import argparse
import os
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError

def parse_category_pages(url_category, page_count):

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

        book_items = soup.find_all(class_='d_book')
        for book_item in book_items:
            book_page = urljoin(url_page, book_item.find_all('a')[1]['href'])
            print(book_page)



def main():

    book_folder = 'books'
    url_txt = 'https://tululu.org/txt.php'
    url_page_book = 'https://tululu.org/b'
    url_scifi_cat = 'https://tululu.org/l55/'

    parse_category_pages(url_scifi_cat, 10)




if __name__ == '__main__':
    main()