from __future__ import annotations
import argparse
from pathlib import Path
import secrets
import gender_guesser.detector as gender
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from argparse import Namespace
import char_dict
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

It CANNOT work without the original texts, as SpaCy will reference the original
placement of characters in the text in order to replace the string for generating
substitutions or performing modifications.
------------------------------------------------------------------------------------
"""

class Label_entities():
    def __init__(self, text: str, char_file_path: Path):
        self.text = text
        self.doc = nlp(self.text)
        self.ch_path = char_file_path
        self.char_list = dict()
        self.male_names, self.female_names = self.read_gender_list("name_gender_dataset.csv") # https://archive.ics.uci.edu/ml/datasets/Gender+by+Name
        self.neutral_names = self.read_unisex_names("unisex-names~2Funisex_names_table.csv") #https://fivethirtyeight.datasettes.com/fivethirtyeight/unisex-names~2Funisex_names_table
        with open(self.ch_path, "r") as f: #todo why couldn't we initialize self.char_list with a function?
            self.char_list = eval(f.read())
        self.local_chars = dict() #Randomized character dictionary

    def read_gender_list(self, gender_file) -> tuple[list,list]:
        male_names = []
        female_names = []
        with open(gender_file, "r")  as f:
            for line in f:
                if line.rstrip("\n").split(",")[1] == "M": #Checks if hte name is male
                    male_names.append(line.rstrip("\n").split(",")[0])
                else:
                    female_names.append(line.rstrip("\n").split(",")[0])

        return male_names, female_names

    def read_unisex_names(self, uni_file) -> list:
        uni_names = []
        with open(uni_file, "r")  as f:
            for line in f:
                uni_names.append(line.rstrip("\n").split(",")[0])

        return uni_names


    def randomize_characters(self, name) -> str or int:
        "Here we randomly assign the values to each character in the file"
        d = gender.Detector()
        if d.get_gender(name) == "male":
            random_label = secrets.choice(self.male_names)
        elif d.get_gender(name) == "female":
            random_label = secrets.choice(self.female_names)
        else:
            random_label = secrets.choice(self.neutral_names)

        return random_label


    def identify_names(self) -> None:
        "Finds each name in the summary and assigns a random value from the UCL values"
        for word in self.doc.ents:
            if word.label_ == "PERSON":
                self.local_chars[word.text] = self.randomize_characters(word.text)


    def replace_names(self) -> None: #todo WILL NOT REPLACE FULL NAMES
        for person in self.local_chars:
            self.text = self.text.replace(person, self.local_chars[person])


    def universal_character_section(self):
        "Character section at the bottom at each summary"
        local_dict = {}
        for person in self.local_chars.keys():
            local_dict[person] = self.char_list[person]

        self.text = self.text + "\n\n" + f"Local characters from Universal Character List: {local_dict}"


    def randomized_character_section(self):
        "Randomized Character Section at the bottom"
        self.text = self.text + "\n\n" + f"Randomized Local characters: {self.local_chars}"


    def create_text_file(self) -> str:
        self.identify_names()
        self.replace_names()
        self.universal_character_section()
        self.randomized_character_section()

        return self.text

#Create a separate file directory
def create_subdirectory(book : Path) -> Path:
    "Creates a new subfolder to store a file of all the subsituted names"

    sub_folder_path = book / f"{book.name.replace(' ', '')}_substituted"
    sub_folder_path.mkdir(parents = True, exist_ok= True) #Creates the subdirectory

    return sub_folder_path


def write_file_sub(filepath: Path, summary: Path, char_file_path: Path) -> None:
    with filepath.open("w", encoding = "utf-8") as f:
        """
       Read the json_object, but create an entirely new file with labeled data
       using create_text_file()
       """
        json_file = open(summary, "r")
        sub_file = Label_entities(json_file.read(), char_file_path)
        f.write(sub_file.create_text_file())
        json_file.close()


def parse_summaries(book: Path, sub_folder_path: Path, char_file_path: Path):
    "For each summary create the file path for it"
    file_list = list((entry for entry in book.iterdir() if entry.is_file() and entry.match('*.txt')))

    for summary in tqdm(file_list, desc = "List of Summaries", unit = "sections"):
        print(summary.name)
        file_name = str(summary.stem) + "_substituted.txt"
        filepath = sub_folder_path / file_name

        write_file_sub(filepath, summary, char_file_path)

def parse_corpus(corpus_path: Path) -> None:
    "Parses through each website, and then each book folder in the BookSum Dataset"

    for website in corpus_path.iterdir(): #i.e. Shmoop, Sparknotes
        for book in tqdm(list(website.iterdir()), desc = "Books list", unit = "Amount of books"): # i.e. Hamlet, Frankenstein
            print(book.name)

            sub_folder_path = create_subdirectory(book) # Create the subfolder

            character_file = char_dict.Universal_Character_list(book, sub_folder_path) #Create the character list
            character_file_path = character_file.generate_file()

            parse_summaries(book, sub_folder_path, character_file_path)  # Write to file


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
        "--file",
        type=str,
        nargs = "+",
        default=None,
        help="Assumes you want a single file that will be modified. CANNOT generate it's own character list")

    parsed_args = parser.parse_args()

    if parsed_args.all is None and parsed_args.book is None and parsed_args.file is None:
        parsed_args.error("At least one of the parsing options is required")

    main(parsed_args)
