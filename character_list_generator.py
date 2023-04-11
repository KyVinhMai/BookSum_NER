import spacy
import json
import re
from pathlib import Path
import secrets
import gender_guesser.detector as gender
spacy.prefer_gpu()
nlp = spacy.load("en_core_web_trf", exclude = ["tagger", "parser", "lemmatizer"]) #Understand pipelines To make this faster
#Generate different seed

class Universal_Character_list():
    def __init__(self, book: Path, sub_folder_path: Path, m_names: list, f_name: list, uni_name: list):
        self.book = book
        self.sf_path = sub_folder_path
        self.male_names, self.female_names = m_names, f_name
        self.neutral_names = uni_name
        self.re_pattern = "St.|\'s|\\+|,|\""
        self.name_exceptions = []
        with open("NameDatasets/name_exceptions.txt", "r") as f:
            for line in f:
                self.name_exceptions.append(line.rstrip())
        self.celebrities = []
        with open("NameDatasets/historical_figures", "r") as f:
            for line in f:
                self.celebrities.append(line.rstrip())

        self.character_counts = {
            "Table_Type": "Character Counts",
            "Characters": dict(),
        }

        self.rand_persons = {
            "Table_Type": "Randomized Names",
            "First Names": dict(),
            "Middle Names": dict(),
            "Last Names": dict()
        }

    def is_name_in_dict(self, single_name: str) -> bool:
        "Combines all the dictionaries in one single dictionary."
        all_name_dicts = self.return_all_dict()
        if single_name in all_name_dicts:
            return True

        return False

    def insert_names_into_dict(self, name, name_tokens: list[str]) -> None:
        """
         If the name type is unknown (whether it may be a first name or last name),
        the name will always then be placed in the first name list.

        This is so that whenever a full name appears, we can use the last name to check
        if it is in the first name list, which will then be removed.
        """
        if len(name_tokens) == 2:

            if name_tokens[0] not in self.rand_persons["First Names"]:
                self.rand_persons["First Names"][name_tokens[0]] = None

            if name_tokens[-1] not in self.rand_persons["Last Names"]:

                "Checks that there are no duplicates in the first name"
                "Ex: a character is introduced with their last name first"
                if name_tokens[-1] in self.rand_persons["First Names"]:
                    self.rand_persons["First Names"].pop(name_tokens[-1])

                self.rand_persons["Last Names"][name_tokens[-1]] = None

        elif len(name_tokens) > 2:
            middle_names = name_tokens[1:-1]
            for middle in middle_names:
                if name not in self.rand_persons["Middle Names"] and self.exceptions_check(name):
                    self.rand_persons["Middle Names"][middle] = None

        # Check the first name of a full name, i.e. Martha of Martha Stewart
        else:
            if not self.is_name_in_dict(name):
                self.rand_persons["First Names"][name] = None

    def tokenize_name(self, name:str) -> list[str]:
        "Splits the name into single tokens and processes them"
        print(name.__repr__(), end= ", ")
        name = re.sub(self.re_pattern, "", name)
        name = re.sub('\n', ' ', name)
        name_tokens = [token for token in name.split(" ") if token and self.exceptions_check(token)]
        print(name_tokens)
        return name_tokens

    def count_character(self, name) -> None:
        """
        We want both the non-line break character name and the normal
        character name to have the same number of counts
        """
        old_name = None
        if "\n" in name:
            old_name = name
            name = "".join([n for n in name.split("\n") if n])

        if old_name:
            if old_name not in self.return_all_dict():
                self.character_counts["Characters"][old_name] = 0
        else:
            if name not in self.return_all_dict():
                self.character_counts["Characters"][name] = 0

        for character in self.character_counts["Characters"].keys():
            if name in character:
                self.character_counts["Characters"][character] += 1

    def exceptions_check(self, name: str) -> bool: #todo recheck since we added more named exceptions
        """
        Passes the name through the exceptions list. Intended to exclude names
        like The Queen of Scots, or God, or even determiners (spacy has an
        issue with removing determiners).
        """
        for word in self.name_exceptions:
            if word == name:
                return False

        return True

    def append_character_list(self) -> None:
        file_list = list((entry for entry in self.book.iterdir() if entry.is_file() and entry.match('*.txt')))

        print(self.book.name, "\n=======================================")
        for summary in file_list:
            raw_file = open(summary, "r")
            doc = nlp(raw_file.read()) #todo only use nlp.pipleline
            print(summary.name)

            for word in doc.ents:
                if word.label_ == "PERSON":
                    name_tokens = self.tokenize_name(word.text)
                    processed_name = " ".join(name_tokens)

                    #insert into character_counts
                    self.count_character(processed_name)

                    #insert into randomized name dictionary
                    self.insert_names_into_dict(processed_name, name_tokens)

            raw_file.close()

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

    def return_all_dict(self) -> dict:
        return self.rand_persons['First Names'] | self.rand_persons['Middle Names'] | self.rand_persons['Last Names']

    def clean(self, name: str) -> str:
        nlp = spacy.load("en_core_web_sm")
        index = name.find("\n")
        temp = [n for n in name.split("\n") if self.exceptions_check(n)]
        print(temp)
        # checks if last word is a verb
        last_word = nlp(temp[-1])[0]
        if last_word.pos_ == "VERB" and last_word.is_lower:
            temp = temp[0:-1]

        temp = list("".join(temp))  # reinsert newline
        temp.insert(index, "\n")
        return "".join(temp)

    def randomize_names(self) -> None:
        """
        For each name in the value-less randomized name, we assign a random label
        """
        for name_dict in ["First Names", "Middle Names", "Last Names"]: #For each name list, we substitute each name with a random one
            for name in self.rand_persons[name_dict]:
                self.rand_persons[name_dict][name] = self.assign_label(name)

    # def remove_figures(self):
    #     all_names = self.return_all_dict()
    #     for name in all_names.keys():
    #         if name in celebrities and self.character_counts[name] < 3:

    def generate_file(self): #-> Path:
        self.append_character_list()
        self.randomize_names()
        # self.remove_figures()

        ch_file_path = self.sf_path / f"{self.book.name.replace(' ', '')}_character_list.txt"

        with ch_file_path.open("w", encoding="utf-8") as f:
            f.write(json.dumps(self.character_counts, indent=4, sort_keys=False))
            f.write("\n\n\n")
            f.write(json.dumps(self.rand_persons, indent=4, sort_keys=False))

        print("Created Character list!")
        return ch_file_path

    def debug(self):
        print(self. male_names)
        print()
        print(self. female_names)
        print()
        print(self. neutral_names)

if __name__ == "__main__":
    # book_test = Path('D:\\Users\kyvin.DESKTOP-ERBCV8T\PycharmProjects\Research-projects\\book_dataset\\booksum\scripts\\finished_summaries\\bookwolf\A Tale of Two Cities')
    # sub_test = Path("D:\\Users\kyvin.DESKTOP-ERBCV8T\PycharmProjects\Research-projects\\book_dataset\\booksum\scripts\\finished_summaries\\bookwolf\A Tale of Two Cities\ATaleofTwoCities_substituted")
    book_test = Path(
        'C:\\Users\\kyvin\\PycharmProjects\\Narrative-Understanding-Dataset\\test_full_book')
    sub_test = Path(
        "C:\\Users\\kyvin\\PycharmProjects\\Narrative-Understanding-Dataset\\test_full_book\\test_full_book_substituted")


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

    male_names, female_names = read_gender_list("NameDatasets/name_gender_dataset.csv")
    neutral_names = read_unisex_names("NameDatasets/unisex-names~2Funisex_names_table.csv")

    c_file = Universal_Character_list(book_test, sub_test, male_names, female_names, neutral_names)
    c_file.generate_file()

