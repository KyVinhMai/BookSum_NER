from __future__ import annotations
import argparse
from pathlib import Path
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from argparse import Namespace
import character_list_generator
from tqdm import tqdm
import spacy
spacy.require_gpu()
nlp = spacy.load("en_core_web_trf", exclude = ["tagger", "parser", "lemmatizer"])
print("INFO: SpaCy successfully initiated")
#todo add gpu accelarator and tqdm

"""
NOTE:
-----------------------------------------------------------------------------------
This script works by placing the substituted summaries within the book folder.

It CANNOT work without the original texts, as character_list_generator.py will 
reference and align with the original placement of characters 
in the text in order to replace the string for doing substitutions.
------------------------------------------------------------------------------------
"""

def read_gender_list(gender_file) -> tuple[list,list]:
    male_names = []
    female_names = []
    with open(gender_file, "r")  as f:
        for line in f:
            if line.rstrip("\n").split(",")[1] == "M": #Checks if the name is male
                male_names.append(line.rstrip("\n").split(",")[0])
            else:
                female_names.append(line.rstrip("\n").split(",")[0])

    return male_names, female_names

def read_unisex_names(uni_file) -> list:
    uni_names = []
    with open(uni_file, "r")  as f:
        for line in f:
            uni_names.append(line.rstrip("\n").split(",")[2])

    return uni_names

male_names, female_names = read_gender_list("name_gender_dataset.csv")
neutral_names = read_unisex_names("unisex-names~2Funisex_names_table.csv")


class Label_entities():
    def __init__(self, text: str, rand_ch_dict:str):
        self.text = text
        self.doc = nlp(self.text)
        self.rand_ch = eval(rand_ch_dict)
        self.first_names = self.rand_ch["First Names"]
        self.middle_names = self.rand_ch["Middle Names"]
        self.last_names = self.rand_ch["Last Names"]

    def replace_names(self) -> None:
        for name_list in [self.first_names, self.middle_names, self.last_names]:
            for person in name_list:
                self.text = self.text.replace(person, name_list[person])

    def randomized_character_section(self):
        "Randomized Character Section at the bottom"
        self.text = self.text + "\n\n" + f"Randomized Local characters: {self.rand_ch}"

    def create_text_file(self) -> str:
        self.replace_names()
        self.randomized_character_section()

        return self.text

#Create a separate file directory
def create_subdirectory(book : Path) -> Path:
    "Creates a new subfolder to store a file of all the subsituted names"

    sub_folder_path = book / f"{book.name.replace(' ', '')}_substituted"
    sub_folder_path.mkdir(parents = True, exist_ok= True) #Creates the subdirectory

    return sub_folder_path


def write_file_sub(filepath: Path, summary: Path, rand_ch_dict) -> None:
    with filepath.open("w", encoding = "utf-16") as f:
        """
       Read the json_object, but create an entirely new file with labeled character
       using create_text_file()
       """
        json_file = open(summary, "r")
        sub_file = Label_entities(json_file.read(), rand_ch_dict)
        f.write(sub_file.create_text_file())
        json_file.close()



def parse_summaries(book: Path, sub_folder_path: Path, rand_ch_dict: Path):
    "For each summary create the file path for it"
    file_list = (entry for entry in book.iterdir() if entry.is_file() and entry.match('*.txt'))

    for summary in tqdm(file_list, desc = "List of Summaries", unit = "sections"):
        print(summary.name)
        file_name = str(summary.stem) + "_substituted.txt"
        filepath = sub_folder_path / file_name

        write_file_sub(filepath, summary, rand_ch_dict)

def parse_corpus(corpus_path: Path) -> None:
    "Parses through each website directory, and then in each book folder in the dataset, create the folder for subsituted books"

    for website in corpus_path.iterdir(): #i.e. Shmoop, Sparknotes
        for book in tqdm(list(website.iterdir()), desc = "Books list", unit = "Amount of books"): # i.e. Hamlet, Frankenstein
            print(book.name)

            sub_folder_path = create_subdirectory(book) # Create the subfolder

            character_file = character_list_generator.Universal_Character_list(book, sub_folder_path, male_names, female_names, neutral_names) #Create the character list
            character_file_path = character_file.generate_file()
            with open(character_file_path, "r") as f:
                character_list = f.read()

            _, random = character_list.split("\n\n\n")

            parse_summaries(book, sub_folder_path, random)  # Write to file


def modify_book(book_path: Path) -> None:
    sub_folder_path = book_path / f"{book_path.name.replace(' ', '')}_substituted"
    character_file_path = sub_folder_path /  f"{book_path.name.replace(' ', '')}_character_list.txt"
    parse_summaries(book_path, sub_folder_path, character_file_path)  # Write to file


def modify_file(file_path: Path) -> None:
    book_path = file_path.parent
    sub_folder_path = book_path / f"{book_path.name.replace(' ', '')}_substituted"
    character_file_path = sub_folder_path /  f"{book_path.name.replace(' ', '')}_character_list.txt"

    write_file_sub(file_path, sub_folder_path, character_file_path)


def main(options: Namespace) -> None:

    if options.all:
        parse_corpus(Path(" ".join(options.all)))

    elif options.book:
        modify_book(Path(" ".join(options.book)))

    else:
        modify_file(Path(" ".join(options.file)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Replace entities with an assigned substitutes")
    option = parser.add_mutually_exclusive_group(required=True)

    option.add_argument(
        "--all",
        type = str,
        nargs = "+",
        default=None,
        help = "Specify the directory to read. Will parse through the entire corpus. Generating character lists and assigning characters." )

    #Modification Options
    option.add_argument(
        "--book",
        type = str,
        nargs = "+",
        default=None,
        help = "Will replace characters within the book. Assumes there already is a character list" ) #error handling for books

    option.add_argument(
        "--single",
        type=str,
        nargs = "+",
        default=None,
        help= "Assumes you want a single file that will be modified. CANNOT generate it's own character list")
    #add random seed
    #Perhaps just create a random character list?

    parsed_args = parser.parse_args()

    if parsed_args.all is None and parsed_args.book is None and parsed_args.file is None:
        parsed_args.error("At least one of the parsing options is required")

    main(parsed_args)
