import requests
from pathlib import Path
import os


def load_book(url, id_book, book_folder):
    payload = {
        "id": id_book,
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    filename = f'{id_book}.txt'
    with open(Path(book_folder, filename), 'wb') as file:
        file.write(response.text.encode())


if __name__ == '__main__':
    book_folder = 'books'
    os.makedirs(book_folder, exist_ok=True)
    print(book_folder)
    url_lib = "https://tululu.org/txt.php"
    for id_book in range(1, 11):
        load_book(url_lib, id_book, book_folder)
