from pathlib import Path
from cleaning_functions import clean_read
from csv import writer
import os


book_list = set()
def collect_book_paths(folder_path: Path) -> iter:
    book_iter = (entry for entry in folder_path.iterdir() if entry.is_file() and entry.match('*.txt'))
    return book_iter

def rename():
    "renames the file and removes the title and author from book"
    pass

def clean_books(book_paths: iter):
    for book_p in book_paths:
        clean_read(book_p)
    # rename()
    pass

def check_word_count(book_path: Path) -> bool:
    "Ensures the books are above the 50,000 word limit"
    num_of_words = 0
    with open(book_path, "r") as file:
        data = file.read()
        lines = data.split()

        # Iterating over every word in
        # lines
        for word in lines:

            # checking if the word is numeric or not
            if not word.isnumeric():
                # Adding the length of the
                # lines in our number_of_words
                # variable
                num_of_words += 1

    return True if 50_000 > num_of_words else False

def move_books_and_clean(book_paths: iter):
    "Moves the books into the subdirectories"
    clean_books(book_paths)

    pass

def create_subdirectories(parent_directory: Path, book_paths: iter):
    "Create book folder and the subsitition folder within it"
    for book_p in book_paths:
        book_folder_path = parent_directory / f"{book_p.name.replace(' ', '')}"
        sub_folder_path = book_folder_path / f"{book_p.name.replace(' ', '')}_substituted"
        book_folder_path.mkdir(parents=True, exist_ok=True)
        sub_folder_path.mkdir(parents=True, exist_ok=True)  # Creates the subdirectory


def write_book_list(path: str):
    with open(os.path.join(path,'book_list.csv'), 'w', encoding='UTF16') as f:
        csv_writer = writer(f)
        for line in book_list:
            csv_writer.writerow([line])

def main(directory: str):

    write_book_list(directory)


if __name__ == "__main__":
    pass
