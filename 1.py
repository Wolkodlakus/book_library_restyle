import requests
from pathlib import Path
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit, unquote


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

    print(str_book[0].strip())
    #for comment in comments:
    #    print(comment)
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


if __name__ == '__main__':
    book_folder = 'books'

    url_txt = 'https://tululu.org/txt.php'
    url_page_book = 'https://tululu.org/b'

    for id_book in range(1, 11):
        try:
            book_data = parse_book_page(url_page_book, id_book)
            filename = f'{id_book}. {book_data["title"]}.txt'
            download_txt(f'{url_txt}?id={id_book}', filename, book_folder)
            download_image(book_data['img_path'])

        except requests.HTTPError:
            print(f'На сайте нет книги {id_book} {book_data["title"]}')
            print()
