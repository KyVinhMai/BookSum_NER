import spacy
import json
import re
from pathlib import Path
import secrets
import gender_guesser.detector as gender
spacy.require_gpu()
nlp = spacy.load("en_core_web_trf", exclude = ["tagger", "parser", "lemmatizer"]) #Understand pipelines To make this faster


class Universal_Character_list():
    def __init__(self, book: Path, sub_folder_path: Path, m_names: list, f_name: list, uni_name: list):
        self.book = book
        self.sf_path = sub_folder_path
        self.male_names, self.female_names = m_names, f_name
        self.neutral_names = uni_name
        self.repattern = "St.|\'s|\\+|,|-|\""

        self.name_exceptions = [] #todo put this into a function
        with open("name_exceptions.txt", "r") as f:
            for line in f:
                self.name_exceptions.append(line.rstrip())

        self.persons = {
            "Table_Type": "Universal Character Names",
            "First Names": dict(),
            "Middle Names": dict(),
            "Last Names": dict()
        }
        self.rand_persons = {
            "Table_Type": "Randomized Names",
            "First Names": dict(),
            "Middle Names": dict(),
            "Last Names": dict()
        }

    def split_name(self, name:str, num: int) -> int:
        "Splits the name into single words"
        def check_if_name_in_dict(single_name) -> bool:
            all_name_dicts = self.persons["First Names"] | self.persons["Middle Names"] | self.persons["Last Names"]
            if single_name in all_name_dicts:
                return False

            return True

        name = re.sub(self.repattern, "", name) # todo WHY IS THIS CAUSING A EMPTY CHARACTER TO APPEAR
        name_tokens = name.split(" ")
        if len(name_tokens)  > 1:

            if name_tokens[0] not in self.persons["First Names"]:
                self.persons["First Names"][name_tokens[0]] = num
                num += 1

            if name_tokens[-1] not in self.persons["Last Names"]:

                if name_tokens[-1] in self.persons["First Names"]:
                    self.persons["First Names"].pop(name_tokens[-1]) # Checks that there are no duplicates in the first name
                    "Theres an issues where the stories introduces a character with their last name first. Which screws up the script"

                self.persons["Last Names"][name_tokens[-1]] = num
                num += 1

        elif len(name_tokens) > 2:
            middle_names = name_tokens[1:-1]

            for middle in middle_names:
                if name not in self.persons["Middle Names"][middle]:
                    num += 1
                    self.persons["Middle Names"][middle] = num

        # Check the first name of a full name, i.e. Martha of Martha Stewart
        else:
            if check_if_name_in_dict(name):
                self.persons["First Names"][name] = num
                num += 1

        return num

    def name_check(self, name: str) -> bool: # todo fix up boy
        """
        Passes the name through the exceptions list. Intended to exclude names
        like The Queen of Scots, or God, or even determiners.
        """
        for word in self.name_exceptions:
            if word in name.lower():
                return False

        return True

    def remove_empty_character(self):
        for name_dict in ["First Names", "Middle Names", "Last Names"]:
            for name in self.persons[name_dict].keys():
                if name == "":
                    self.persons[name_dict].pop("")
                    break

    def append_universal_character_list(self) -> None:
        num = 0
        file_list = list((entry for entry in self.book.iterdir() if entry.is_file() and entry.match('*.txt')))

        print(self.book.name, "\n=======================================")
        for summary in file_list:
            raw_file = open(summary, "r")
            doc = nlp(raw_file.read()) #todo only use nlp.pipleline
            print(summary.name)

            for word in doc.ents:
                if word.label_ == "PERSON" and self.name_check(word.text):
                    increment = self.split_name(word.text, num)
                    num = increment

            raw_file.close()

        self.remove_empty_character()

    def assign_label(self, name) -> str or int:
        "Here we randomly assign the labels to each character for the randomized list"
        d = gender.Detector()
        if d.get_gender(name) == "male":
            random_label = secrets.choice(self.male_names)
        elif d.get_gender(name) == "female":
            random_label = secrets.choice(self.female_names)
        else:
            random_label = secrets.choice(self.neutral_names)

        return random_label

    def randomize_names(self) -> None:
        "Finds each name in the character_list and assigns a random label"
        for name_dict in ["First Names", "Middle Names", "Last Names"]: #For each name list, we substitute each name with a random one
            for name in self.persons[name_dict].keys():
                self.rand_persons[name_dict][name] = self.assign_label(name)

    def generate_file(self) -> Path:
        self.append_universal_character_list()
        self.randomize_names()

        ch_file_path = self.sf_path / f"{self.book.name.replace(' ', '')}_character_list.txt"

        with ch_file_path.open("w", encoding = "utf-8") as f:
            f.write(json.dumps(self.persons, indent = 4, sort_keys = False))
            f.write("\n\n\n")
            f.write(json.dumps(self.rand_persons, indent = 4, sort_keys = False))

        print("Created Character list!")
        return ch_file_path

    def debug(self):
        print(self. male_names)
        print()
        print(self. female_names)
        print()
        print(self. neutral_names)

if __name__ == "__main__":
    book_test = Path('D:\\Users\kyvin.DESKTOP-ERBCV8T\PycharmProjects\Research-projects\\book_dataset\\booksum\scripts\\finished_summaries\\bookwolf\A Tale of Two Cities')
    sub_test = Path("D:\\Users\kyvin.DESKTOP-ERBCV8T\PycharmProjects\Research-projects\\book_dataset\\booksum\scripts\\finished_summaries\\bookwolf\A Tale of Two Cities\ATaleofTwoCities_substituted")



    def read_gender_list(gender_file) -> tuple[list,list]:
        male_names = []
        female_names = []
        with open(gender_file, "r")  as f:
            for line in f:
                if line.rstrip("\n").split(",")[1] == "M": #Checks if hte name is male
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

    c_file = Universal_Character_list(book_test, sub_test, male_names, female_names, neutral_names)
    c_file.generate_file()
