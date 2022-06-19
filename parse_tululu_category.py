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

def main():

    book_folder = 'books'
    url_txt = 'https://tululu.org/txt.php'
    url_page_book = 'https://tululu.org/b'
    url_scifi_cat = 'https://tululu.org/l55/'

    params = ''
    response = requests.get(url_scifi_cat, params=params)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')

    book_page = urljoin(url_scifi_cat, soup.find(class_='d_book').find_all('a')[1]['href'])

    pprint(book_page)


if __name__ == '__main__':
    main()