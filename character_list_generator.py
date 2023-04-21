import spacy
import json
import logging
import re
from pathlib import Path
import secrets
import gender_guesser.detector as gender

#Generate different seed

spacy.prefer_gpu()

nlp = spacy.load("en_core_web_trf")

### The current spacy version gives errors if any of the below is included. For some reason, it does not have a "parser" component, for example.
#nlp = spacy.load("en_core_web_trf",
#                 exclude=["attribute_ruler", "lemmatizer"])  # Understand pipelines To make this faster

#nlp = spacy.load("en_core_web_trf",
#                 exclude=["tagger", "parser", "lemmatizer"])  # Understand pipelines To make this faster

#pipe = spacy.load("en_core_web_sm")

from utils.read_name_files import read_gender_list, read_unisex_names, read_exceptions, read_figures

male_names, female_names = read_gender_list()
neutral_names, h_figures, name_exceptions = read_unisex_names(), read_figures(), read_exceptions()



"Logging Configuration"
logging.basicConfig(
    level=logging.INFO,
    filename= "characters.log",
    filemode= "w"
)

class Universal_Character_list():
    def __init__(self, book: Path, sf_path: Path, m_names: list, f_name: list,
                 uni_name: list, n_exceptions, h_figures):
        self.book = book
        self.sf_path = sf_path
        self.male_names, self.female_names = m_names, f_name
        self.neutral_names = uni_name
        self.re_pattern = "St\.|\'s|\\+|,|\""
        self.name_exceptions = n_exceptions
        self.celebrities = h_figures

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

    def all_dict(self) -> dict:
        "Combines all the dictionary names together"
        return self.rand_persons['First Names'] | self.rand_persons['Middle Names'] | self.rand_persons['Last Names']

    def insert_names_into_dict(self, name, name_tokens: list[str]) -> None:
        """
         If the name type is unknown (whether it may be a first name or last name),
        the name will always then be placed in the first name list.

        This is so that whenever a full name appears, we can use the last name to check
        if it is in the first name list, which will then be removed.
        """
        name = name.lower()
        name_tokens = [t.lower() for t in name_tokens]

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
                if name not in self.rand_persons["Middle Names"]:
                    self.rand_persons["Middle Names"][middle] = None

        # Check the first name of a full name, i.e. Martha of Martha Stewart
        else:
            if name not in self.all_dict():
                self.rand_persons["First Names"][name] = None

    def rm_verb(self, name_tokens: list[str]) -> list[str]:
        "Line breaks cause verbs to be appended to names... Wilton\ngo"
        # checks if last word is a verb
        with nlp.select_pipes(disable=["ner", "parser"]):
            last_word = nlp(name_tokens[-1])[0]
            if last_word.pos_ != "NOUN" and last_word.is_lower:
                name_tokens = name_tokens[0:-1]

        return name_tokens

    def tokenize_name(self, name:str) -> list[str]:
        "Splits the name into single tokens and processes them"
        logging.info(f"{name.__repr__()}")
        name = re.sub(self.re_pattern, "", name)
        name = re.sub('\n', ' ', name)
        name_tokens = [token for token in name.split(" ") if token and self.exceptions_check(token)]
        return name_tokens

    def count_character(self, name_tokens:[str]) -> None:
        """
        We want both the non-line break character name and the normal
        character name to have the same number of counts
        """
        for name in name_tokens:
            try:
                self.character_counts["Characters"][name] += 1
            except KeyError:
                self.character_counts["Characters"][name] = 1

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
            doc = nlp(raw_file.read())
            print(summary.name)

            for word in doc.ents:
                if word.label_ == "PERSON":
                    try:
                        name_tokens = self.tokenize_name(word.text)
                        name_tokens = self.rm_verb(name_tokens)
                    except IndexError:
                        "rm_verb tried to index into an empty list"
                        continue
                    finally:
                        if name_tokens == []:
                            continue

                    logging.info(f"{name_tokens}")
                    processed_name = " ".join(name_tokens)
                    #insert into character_counts
                    self.count_character(name_tokens)
                    #insert into randomized name dictionary
                    self.insert_names_into_dict(processed_name, name_tokens)

            raw_file.close()

    def assign_label(self, name) -> tuple[str, str]:
        "Here we randomly assign the labels to each character for the randomized list"
        d = gender.Detector()
        if d.get_gender(name) == "male":
            gen = "male"
            random_label = secrets.choice(self.male_names)
        elif d.get_gender(name) == "female":
            gen = "female"
            random_label = secrets.choice(self.female_names)
        else:
            gen = "neutral"
            random_label = secrets.choice(self.neutral_names)

        return random_label, gen

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
        print(self.rm_verb(["Edward"]))

class CharacterProcessor():
    def __init__(self, book: str, m_names: list, f_name: list,
                 uni_name: list, n_exceptions, h_figures):
        self.book = book
        self.male_names, self.female_names = m_names, f_name
        self.neutral_names = uni_name
        self.re_pattern = "St\.|\'s|\\+|,|\""
        self.name_exceptions = n_exceptions
        self.celebrities = h_figures

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

    def all_dict(self) -> dict:
        "Combines all the dictionary names together"
        return self.rand_persons['First Names'] | self.rand_persons['Middle Names'] | self.rand_persons['Last Names']

    def insert_names_into_dict(self, name, name_tokens: list[str]) -> None:
        """
         If the name type is unknown (whether it may be a first name or last name),
        the name will always then be placed in the first name list.

        This is so that whenever a full name appears, we can use the last name to check
        if it is in the first name list, which will then be removed.
        """

        name = name.lower()
        name_tokens = [t.lower() for t in name_tokens]

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
                if name not in self.rand_persons["Middle Names"]:
                    self.rand_persons["Middle Names"][middle] = None

        # Check the first name of a full name, i.e. Martha of Martha Stewart
        else:
            if name not in self.all_dict():
                self.rand_persons["First Names"][name] = None

    def rm_verb(self, name_tokens: list[str]) -> list[str]:
        "Line breaks cause verbs to be appended to names... Wilton\ngo"
        # checks if last word is a verb
        with nlp.select_pipes(disable=["ner", "parser"]):
            last_word = nlp(name_tokens[-1])[0]
            if last_word.pos_ != "NOUN" and last_word.is_lower:
                name_tokens = name_tokens[0:-1]

        return name_tokens

    def tokenize_name(self, name:str) -> list[str]:
        "Splits the name into single tokens and processes them"
        logging.info(f"{name.__repr__()}")
        name = re.sub(self.re_pattern, "", name)
        name = re.sub('\n', ' ', name)
        name_tokens = [token for token in name.split(" ") if token and self.exceptions_check(token)]
        return name_tokens

    def count_character(self, name_tokens:[str]) -> None:
        """
        We want both the non-line break character name and the normal
        character name to have the same number of counts
        """
        for name in name_tokens:
            try:
                self.character_counts["Characters"][name] += 1
            except KeyError:
                self.character_counts["Characters"][name] = 1

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

        doc = nlp(self.book)

        for word in doc.ents:
            if word.label_ == "PERSON":
                try:
                    name_tokens = self.tokenize_name(word.text)
                    name_tokens = self.rm_verb(name_tokens)
                except IndexError:
                    "rm_verb tried to index into an empty list"
                    continue
                finally:
                    if name_tokens == []:
                        continue

                logging.info(f"{name_tokens}")
                processed_name = " ".join(name_tokens)
                #insert into character_counts
                self.count_character(name_tokens)
                #insert into randomized name dictionary
                self.insert_names_into_dict(processed_name, name_tokens)

    def assign_label(self, name) -> tuple[str, str]:
        "Here we randomly assign the labels to each character for the randomized list"
        d = gender.Detector()
        if d.get_gender(name) == "male":
            gen = "male"
            random_label = secrets.choice(self.male_names)
        elif d.get_gender(name) == "female":
            gen = "female"
            random_label = secrets.choice(self.female_names)
        else:
            gen = "neutral"
            random_label = secrets.choice(self.neutral_names)

        return random_label, gen

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

    def debug(self):
        print(self.rm_verb(["Edward"]))


def get_counts_and_subs(book):
    cl = CharacterProcessor(book, male_names, female_names, neutral_names, name_exceptions, h_figures)
    cl.append_character_list()
    cl.randomize_names()

    return  cl.character_counts, cl.rand_persons,
if __name__ == "__main__":


    if False:
        book_test = Path(
            'D:\\Research_Projects\\ArsenyProjects\\neurlips\\test_full_book')
        sub_test = Path(
            "D:\\Research_Projects\\ArsenyProjects\\neurlips\\test_full_book\\test_full_book_substituted")


        c_file = Universal_Character_list(book_test, sub_test, male_names, female_names,
                                          neutral_names,
                                          name_exceptions,
                                          h_figures)
        c_file.generate_file()

    test_str = "This is a test string with fake characters Becky and John."
    ch_counts, rand_ch = get_counts_and_subs(book=test_str)

    with open("Data/RawBooks/ScifiExampleRaw.txt", "r") as f:
        booktext = f.read()

    char_replacement = get_counts_and_subs(book=booktext)

