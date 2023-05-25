import os
import shutil
from pathlib import Path

def split_folder(folder_path):
    def return_id(elem):
        return int(elem.stem) if "-" not in elem.stem else int(elem.stem.split("-")[0])

    folder_path = Path(folder_path)
    parent_path = Path(folder_path).parents[0]

    # Create two new folders for split contents
    left_folder = parent_path / "Ky_books3"
    right_folder = parent_path / "Arseny_books3"
    left_folder.mkdir(exist_ok=True)
    right_folder.mkdir(exist_ok=True)

    # Get the list of files in the folder
    files = [file.name for file in sorted(folder_path.iterdir(), key=return_id)]
    total_files = len(files)

    # Calculate the number of files for each side
    files_per_side = total_files // 2

    # Move files to the left folder
    for i in range(files_per_side):
        file_name = str(files[i])
        file_path = folder_path / file_name
        destination = left_folder / file_name
        print(left_folder)
        shutil.move(file_path, destination)
    print("Ky's book complete")

    # Move remaining files to the right folder
    for i in range(files_per_side, total_files):
        file_name = str(files[i])
        file_path = folder_path / file_name
        destination = right_folder / file_name
        print(file_name)
        shutil.move(file_path, destination)
    print("Arseny's book complete")


    print("Folder split completed successfully.")


# Split the folder
split_folder(r"C:\Users\kyvin\PycharmProjects\Narrative-Understanding-Dataset\PG_book_processing\processed_files2\unique_authors")