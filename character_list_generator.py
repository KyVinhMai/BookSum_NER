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
        self.re_pattern = "St.|\'s|\\+|,|-|\""
        self.name_exceptions = []
        with open("NameDatasets/name_exceptions.txt", "r") as f:
            for line in f:
                self.name_exceptions.append(line.rstrip())

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
        all_name_dicts = self.rand_persons['First Names'] | self.rand_persons['Middle Names'] | self.rand_persons['Last Names']
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

    def split_name(self, name:str) -> list[str]:
        "Splits the name into single tokens"
        name = re.sub(self.re_pattern, "", name) #todo Strangely causes an empty character to appear
        name_tokens = [token for token in name.split(" ") if token]

        return name_tokens

    def count_character(self, name) -> None:
        if "\n" in name:
            name = "".join([n for n in name.split("\n") if n])
            
        for character in self.character_counts["Characters"].keys():
            if name in character:
                self.character_counts["Characters"][character] += 1
        else:
            self.character_counts["Characters"][name] = 1

    def exceptions_check(self, name: str) -> bool: #todo recheck since we added more named exceptions
        """
        Passes the name through the exceptions list. Intended to exclude names
        like The Queen of Scots, or God, or even determiners (spacy has an
        issue with removing determiners).
        """
        for word in self.name_exceptions:
            if word in name:
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
                if word.label_ == "PERSON" and self.exceptions_check(word.text):
                    #insert into character_counts
                    self.count_character(word.text)

                    #insert into randomized name dictionary
                    name_tokens = self.split_name(word.text)
                    self.insert_names_into_dict(word.text, name_tokens)

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

    def query_all_rand_dict(self, name:str) -> str:
        """
        A helper function to retrieve the value from the names dictionary as
        the dictionary will be continuously updated.
        """
        all_dict = self.rand_persons['First Names'] | self.rand_persons['Middle Names'] | self.rand_persons['Last Names']
        return all_dict[name]

    def label_exists(self, name: str) -> bool:
        "Checks if label exists"
        all_name_dicts = self.rand_persons['First Names'] | self.rand_persons['Middle Names'] | self.rand_persons['Last Names']
        if all_name_dicts[name]:
            return True

        return False


    def randomize_names(self) -> None:
        """
        For each name in the value-less randomized name, we assign a random label

        Note:
        We have to deal with names which have line breaks in them, as the script
        requires each name to be unique. We have to deal with 3 different instances
        of the same entity.

        Ex. "Jimmy\nOlyphant", "Jimmy", "Olyphant"

        When coming across a line break name, we check if the associated names
        already have random labels assigned. Otherwise, create the random label and
        assign them there (so that we no longer have to process it)
        """
        for name_dict in ["First Names", "Middle Names", "Last Names"]: #For each name list, we substitute each name with a random one
            for name in self.rand_persons[name_dict].copy():

                if "\n" in name: #name with line break exception
                    name_segments = [word for word in name.split("\n") if word]
                    for n in name_segments:

                        if self.exceptions_check(n):

                            if self.label_exists(n): #todo if name has label | fix semantics of the truth value for this
                                index = name_segments.index(n)
                                name_segments[index] = self.query_all_rand_dict(n)

                            else:
                                new_name = self.assign_label(n) #create new name
                                self.rand_persons[name_dict][n] = new_name #register
                                index = name_segments.index(n)
                                name_segments[index] = new_name #replace

                    name_segments.insert(1, "\n")#reinsert the line break
                    new_name = "".join(name_segments)
                    self.rand_persons[name_dict][name] = new_name

                else:
                    if self.rand_persons[name_dict][name] is None and self.exceptions_check(name):
                        self.rand_persons[name_dict][name] = self.assign_label(name)

    def generate_file(self) -> Path:
        self.append_character_list()
        self.randomize_names()

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
        'D:\\Research_Projects\\ArsenyProjects\\test_full_book')
    sub_test = Path(
        "D:\\Research_Projects\\ArsenyProjects\\test_full_book\\My_First_Years_book_substituted")


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

