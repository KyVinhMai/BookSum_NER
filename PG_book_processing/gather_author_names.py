from pathlib import Path
import json
from cleaning_functions import clean_read

book_table = dict()
test_dict = {
    "Mark Twain": ["5060:The Adventures of Fin and Tech"]
}

def collect_book_paths(folder_path: str) -> iter:
    def return_id(elem):
        return int(elem.stem) if "-" not in elem.stem else int(elem.stem.split("-")[0])

    path = Path(folder_path)
    book_iter = [entry for entry in path.iterdir() if entry.is_file() and entry.match('*.txt')]
    book_iter = sorted(book_iter, key=return_id)
    return book_iter

def record_info(book_iter: iter):
    """
    copied_book_paths: NEEDS to be the copied books path and not the
    original book paths
    """
    for book_p in book_iter:
        author, title, _ = clean_read(str(book_p))
        ID = book_p.stem
        print(ID, author)
        if author in book_table:
            book_table[author].append(f"{ID}||{author}||{title}")
        else:
            book_table[author] = list()
            book_table[author].append(f"{ID}||{author}||{title}")

def write_book_list(path: str):
    """
    Writes reference book list with File ID, Book Title, and Author Name
    """
    with open(f"{path}\\unique_author_list.txt", "w", encoding="utf-8") as f:
        f.write(json.dumps(book_table, indent=4, sort_keys=False))

    print("Book Table!")

def main(folder_path:str):
    book_iter = collect_book_paths(folder_path)
    record_info(book_iter)
    write_book_list(folder_path)

if __name__ == "__main__":
    main(r"C:\Users\kyvin\PycharmProjects\Narrative-Understanding-Dataset\PG_book_processing\processed_files2\Arseny_books3")