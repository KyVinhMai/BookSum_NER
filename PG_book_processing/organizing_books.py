from pathlib import Path
from cleaning_functions import clean_read

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
    with open(book_path, "r") as file:
        file.read()

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

if __name__ == "__main__":
    pass
