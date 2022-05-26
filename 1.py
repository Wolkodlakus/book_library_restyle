import requests
from pathlib import Path
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit, urlparse, unquote

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

    return str_book[0].strip(), str_book[1].strip(), img_path


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
    #filepath = urlsplit(unquote(url_string)).path
    filepath = urlparse(unquote(url_string)).path
    _, filename = os.path.split(filepath)
    return filename

def download_image(url, folder='images/', params=''):
    name_img = find_filename_in_url(url)
    #name_img = urlsplit(url, )
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url_img, params=params)
    response.raise_for_status()
    with open(Path(folder, name_img), 'wb') as file:
        file.write(response.content)

if __name__ == '__main__':
    book_folder = 'books'

    url_txt = 'https://tululu.org/txt.php'
    url_page_book = 'https://tululu.org/b'


    for id_book in range(1, 11):
        try:
            title, _, url_img = parse_book_page(url_page_book, id_book)
            filename = f'{id_book}. {title}.txt'
            download_txt(f'{url_txt}?id={id_book}', filename, book_folder)
            download_image(url_img)

        except requests.HTTPError:
            print(f'На сайте нет книги {id_book} {title}')

