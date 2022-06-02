#!/usr/bin/python
"""
Скрипт для скачивания книг из библиотеки tululu.org
"""
import argparse
import os
import time
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def parse_book_page(page, url):
    """Функция для парсинга названия и автора книги.
    Args:
        page (str): html содержание страницы
        url (str): Cсылка на сайт, с которого хочется скачать.
    Returns:
        dict: словарь с характеристиками книги."""
    soup = BeautifulSoup(page, 'lxml')
    str_book = soup.find('h1').text.split(" :: ")
    img_path = urljoin(url, soup.find(class_='bookimage').find('img')['src'])

    comments = [comment.text for comment in soup.find(id='content').find_all('span', class_='black')]
    genres = [genre.text for genre in soup.find('span', class_='d_book').find_all('a')]

    return {
        'title': str_book[0].strip(),
        'author': str_book[1].strip(),
        'genres': genres,
        'img_path': img_path,
        'comments': comments
    }


def download_txt(url, filename, folder='books/', params=''):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
        params (dict): параметры для GET запроса, по умолчанию пустая строка
    Returns:
        str: Путь до файла, куда сохранён текст."""
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    path_file = Path(folder, sanitize_filename(filename))
    with open(path_file, 'wb') as file:
        file.write(response.text.encode())
    return path_file


def find_filename_in_url(url_string):
    """Поиск имени файла в url"""
    filepath = urlsplit(unquote(url_string)).path
    _, filename = os.path.split(filepath)
    return filename


def download_image(url, folder='images/', params=''):
    """Функция для скачивания картинок.
        Args:
            url (str): Cсылка на сайт, с которого хочется скачать.
            folder (str): директория для сохранения картинок, по умолчанию images/
            params (str): параметры для GET запроса, по умолчанию пустая строка
    """
    img_name = find_filename_in_url(url)
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url, params=params)
    response.raise_for_status()
    with open(Path(folder, img_name), 'wb') as file:
        file.write(response.content)


def create_args_parser():
    parser = argparse.ArgumentParser(description='Программа для скачивания книг с .. по ..')
    parser.add_argument('start_id', nargs='?', default='1', help='С какого номера книги начинать', type=int)
    parser.add_argument('end_id', nargs='?', default='10', help='Каким номером заканчивать', type=int)
    return parser


def main():
    parser = create_args_parser()
    args = parser.parse_args()
    start = args.start_id
    end = args.end_id

    book_folder = 'books'
    url_txt = 'https://tululu.org/txt.php'
    url_main = 'https://tululu.org'

    print(f'Программа начинает скачивание книг с {start} по {end}')
    id_book = start
    attempts = 0
    while (id_book <= end) and (attempts < 8):
        book_properties = None
        try:
            response = requests.get(f'{url_main}/b{id_book}/')
            response.raise_for_status()
            check_for_redirect(response)
            book_properties = parse_book_page(
                response.text,
                url_main
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
            id_book += 1
            attempts = 0
        except requests.HTTPError:
            print(f'На сайте нет книги {id_book} ', end='')
            if book_properties:
                print(book_properties["title"])
            print(end='\n')
            id_book += 1
            attempts = 0
        except requests.ConnectionError:
            print(f'Обрыв связи на книге {id_book}. Попытка {attempts+1}')
            time.sleep(2**attempts)
            attempts += 1
    if attempts == 8:
        print(f'Не удалось восстановить связь. Книги с {id_book} не скачаны')


if __name__ == '__main__':
    main()
