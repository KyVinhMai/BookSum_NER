from pathlib import Path
from cleaning_functions import clean_read
from csv import writer
import os
import shutil

book_list = set()

def collect_book_paths(folder_path: str) -> iter:
    path = Path(folder_path)
    book_iter = (entry for entry in path.iterdir() if entry.is_file() and entry.match('*.txt'))
    return book_iter

def clean_books(copied_book_paths: iter):
    """
    copied_book_paths: NEEDS to be the copied books path and not the
    original book paths
    """
    for book_p in copied_book_paths:
        auth, title, cleaned_data = clean_read(str(book_p))
        ID = book_p.stem
        print(ID)
        book_list.add((ID, title, auth))
        with open(book_p, "w", encoding="latin-1") as file:
            file.write(cleaned_data)

def check_word_count(book_path: Path) -> bool:
    "Ensures the books are above the 50,000 word limit"
    num_of_words = 0
    with open(book_path, "r", encoding="latin-1") as file:
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

    return True if num_of_words > 50_000 else False

def copy_books(file, destination: str):
    "Moves the books into the subdirectories"
    shutil.copy2(file, destination)

def write_book_list(path: str):
    """
    Writes reference book list with File ID, Book Title, and Author Name
    """
    with open(os.path.join(path,'book_list.csv'), 'w', encoding='utf8') as f:
        csv_writer = writer(f, lineterminator= '\n')
        csv_writer.writerow(["ID, Book Title, Author Name"])
        for line in book_list:
            csv_writer.writerow(line)

def main(path:str):
    original = path + "\\books_batch2"
    filter = path + "\\over_word_count"
    destination = path + "\\cleaned_books"

    book_iter = collect_book_paths(original)

    for book in book_iter:
        if check_word_count(book):
            copy_books(book, filter)

    print("Books over the word count, Done!")
    book_word_count  = collect_book_paths(filter)
    for book in book_word_count:
        copy_books(book, destination)

    copied_bk_iter = collect_book_paths(destination)
    clean_books(copied_bk_iter)
    write_book_list(destination)

if __name__ == "__main__":
    main(r"C:\Users\kyvin\PycharmProjects\Narrative-Understanding-Dataset\PG_book_processing\books")
