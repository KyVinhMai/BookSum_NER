import re
from typing import Pattern

def template(name) -> str:
    return f"(){name}(\W)"

def last_ntemplate(last_name) -> str:
    return f"(){last_name}(\W)"
"""
for name, rand_name in First_Middle_dictionary:
    pattern = f"()name(\W)"
    self.text = re.sub(pattern, f"\\1{rand_name}\\1", self.text)

"""


#name_dict: dict[str:str]
def preprocess_name_dictionary(firsts,middles,lasts) -> Pattern[str]:
    """
    Converts dictionary names into a regex pattern
    references code from
    https://gist.github.com/carlsmith/b2e6ba538ca6f58689b4c18f46fef11c

    Ex: (Harry)(\W)| N.(\W)|(Potter)(\W)
    """
    substrings = list(map(template, firsts.keys() + middles.keys()))
    last_strings = list(map(last_ntemplate, lasts.keys()))
    regex = re.compile('|'.join(substrings + last_strings))

    return regex

def replace(string, substitutions):

    substrings = list(substitutions.keys())
    # regex = re.compile('|'.join(map(re.escape, substrings)))
    regex = re.compile('( )foo(\W)')
    # return regex.sub(lambda match: substitutions[match.group(0)], string)
    return regex.sub("\\1FOO\\1",string)

if __name__ == "__main__":
    string = "spam foo bar foo bar spam"
    substitutions = {"foo": "FOO", "bar": "BAR"}
    output = replace(string, substitutions)
    print(output)

    # regex = r"([a-zA-Z]+)|(\d+)"
    #
    # match = re.findall(regex, "I was born on June 24")
    # print(match)

