from pathlib import Path
import json
from cleaning_functions import clean_read

unique_authors = dict()

def collect_book_paths(folder_path: str) -> iter:
    path = Path(folder_path)
    book_iter = (entry for entry in path.iterdir() if entry.is_file() and entry.match('*.tagseparated'))
    return book_iter

# def main(destination:str, reference_folder: str):
#     with open(reference_folder + r"\file_name_list.txt") as f:
#         author_dict = eval(f.read())
#
#     book_iter = collect_book_paths(destination)
#
#     for file_name in book_iter:
#         ID = file_name.stem
#         unique_authors[ID] = author_dict[ID]
#
#     with open(f"{destination}\\file_name_list.txt", "w", encoding="utf-8") as f:
#         f.write(json.dumps(unique_authors, indent=4, sort_keys=False))
#
#     print("Book Table!")

def main(destination:str, reference_folder: str):
    book_iter = collect_book_paths(destination)

    for file_name in book_iter:
        ID = file_name.stem
        author, title, _ = clean_read(str(reference_folder)+ "\\" + ID + ".txt")
        unique_authors[ID] = f"{author}||{title}"

    with open(f"{destination}\\file_name_list.txt", "w", encoding="utf-8") as f:
        f.write(json.dumps(unique_authors, indent=4, sort_keys=False))

    print("Book Table!")



if __name__ == "__main__":
    main(r"C:\Users\kyvin\PycharmProjects\Narrative-Understanding-Dataset\PG_book_processing\cross_reference\TrainSet1000",
         r"C:\Users\kyvin\PycharmProjects\Narrative-Understanding-Dataset\PG_book_processing\cross_reference\f1000_reference")