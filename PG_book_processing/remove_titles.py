from pathlib import Path
from cleaning_functions import clean_read
import os
import sys


def collect_book_paths(folder_path: str) -> list:
    path = Path(folder_path)
    book_list = [str(entry) for entry in path.iterdir() if entry.is_file() and entry.match('*.txt')]
    return book_list

def main(folder: str):
    with open(r"processed_files\unique_authors\unique_author_list.txt") as f:
        author_dict = eval(f.read())

    title_list = [folder + "\\" + title[0].split("||")[0] + ".txt" for title in author_dict.values()]
    book_list = collect_book_paths(folder)
    title_list.append(r"C:\\Users\\kyvin\\PycharmProjects\\Narrative-Understanding-Dataset\\PG_book_processing\\processed_files\\unique_authors\\unique_author_list.txt")

    for file in book_list:
        if file not in title_list:
            print(file)
            os.remove(file)
    print("Done!")

main(r"C:\Users\kyvin\PycharmProjects\Narrative-Understanding-Dataset\PG_book_processing\processed_files\unique_authors")
