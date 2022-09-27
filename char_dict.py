import spacy
import json
import re
from pathlib import Path
spacy.require_gpu()
nlp = spacy.load("en_core_web_trf", exclude = ["tagger", "parser", "lemmatizer"]) #Understand pipelines To make this faster

class Universal_Character_list():
    def __init__(self, book: Path, sub_folder_path: Path):
        self.book = book
        self.sf_path = sub_folder_path
        self.persons = dict()
        self.repattern = "St.|\'s|\\|,|-|\"| and"

    def split_name(self, name: str, num) -> int:
        "Splits the name into single words"

        # Check the first name of a full name, i.e. Martha of Martha Stewart
        if " " in name:
            names = name.split(" ")
            for n in names:
                n = re.sub(self.repattern, "", n)
                self.persons[n] = num
                num += 1

        else:
            name = re.sub(self.repattern, "", name)
            self.persons[name] = num
            num += 1

        return num

    def append_character_list(self) -> None:
        num = 0
        file_list = list((entry for entry in self.book.iterdir() if entry.is_file() and entry.match('*.txt')))

        print(self.book.name, "\n=======================================")
        for summary in file_list:
            raw_file = open(summary, "r")
            doc = nlp(raw_file.read())
            print(summary.name)

            for word in doc.ents:
                if word.label_ == "PERSON":
                    increment = self.split_name(word.text, num)
                    num = increment

            raw_file.close()

    def generate_file(self) -> Path:
        self.append_character_list()

        ch_file_path = self.sf_path / f"{self.book.name.replace(' ', '')}_character_list.txt"

        with ch_file_path.open("w", encoding = "utf-8") as f:
            f.write("Universal Single Name Character List:")
            f.write(json.dumps(self.persons, indent = 4, sort_keys = False))

        print("Created Character list!")
        return ch_file_path

if __name__ == "__main__":
    book_test = Path('D:\\Users\kyvin.DESKTOP-ERBCV8T\PycharmProjects\Research-projects\\book_dataset\\booksum\scripts\\finished_summaries\\bookwolf\A Tale of Two Cities')
    sub_test = Path("D:\\Users\kyvin.DESKTOP-ERBCV8T\PycharmProjects\Research-projects\\book_dataset\\booksum\scripts\\finished_summaries\\bookwolf\A Tale of Two Cities\ATaleofTwoCities_substituted")

    c_file = Universal_Character_list(book_test, sub_test)
    c_file.generate_file()