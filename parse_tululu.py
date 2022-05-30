import argparse
import os
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    return response.history


def parse_book_page(url, id_book):
    """Функция для парсинга названия и автора книги.
    Args:
        url (str): Cсылка на сайт, с которого хочется скачать.
        id_book (int): номер книги.
    Returns:
        str, str: Название и автор книги."""
    response = requests.get(f'{url}{id_book}/')
    response.raise_for_status()
    if check_for_redirect(response):
        raise requests.HTTPError
    soup = BeautifulSoup(response.text, 'lxml')
    str_book = soup.find('h1').text.split(" :: ")
    img_path = urljoin(url, soup.find(class_='bookimage').find('img')['src'])
    comments = []
    for comment in soup.find(id='content').find_all('span', class_='black'):
        comments.append(comment.text)
    comments_soup = soup.find(id='content').find_all('span', class_='black')
    genres = []
    for genre in soup.find('span', class_='d_book').find_all('a'):
        genres.append(genre.text)

    print(f'Заголовок: {str_book[0].strip()}')
    print(f'Автор: {str_book[0].strip()}')
    print(f'Жанры: {genres}')
    print(f'{len(comments)} комментарий/я/ев: ')
    for i, comment in enumerate(comments):
        print(f'{i+1}. {comment}')
    print(genres)
    print()

    return {
        'title': str_book[0].strip(),
        'author': str_book[1].strip(),
        'genres': genres,
        'img_path': img_path,
        'comments': comments
    }


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    if check_for_redirect(response):
        raise requests.HTTPError
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
    name_img = find_filename_in_url(url)
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url, params=params)
    response.raise_for_status()
    with open(Path(folder, name_img), 'wb') as file:
        file.write(response.content)


def create_args_parser():
    parser = argparse.ArgumentParser(description='Программа для скачивания книг с .. по ..')
    parser.add_argument('start_id', nargs='?', default='1', help='С какого номера книги начинать', type=int)
    parser.add_argument('end_id', nargs='?', default='10', help='Каким номером заканчивать', type=int)

    return parser


if __name__ == '__main__':
    parser = create_args_parser()
    args = parser.parse_args()

    book_folder = 'books'

    url_txt = 'https://tululu.org/txt.php'
    url_page_book = 'https://tululu.org/b'

    start = args.start_id
    end = args.end_id

    print(f'Программа начинает скачивание книг с {start} по {end}')
    for id_book in range(start, end+1):
        book_data = None
        try:
            book_data = parse_book_page(url_page_book, id_book)
            filename = f'{id_book}. {book_data["title"]}.txt'
            download_txt(f'{url_txt}?id={id_book}', filename, book_folder)
            download_image(book_data['img_path'])

        except requests.HTTPError:
            print(f'На сайте нет книги {id_book} ', end='')
            if not(book_data is None):
                print(book_data["title"])
            print(end='\n')
