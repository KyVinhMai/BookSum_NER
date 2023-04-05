import re

def apply_white_space(name):
    return f" {name}(\s|\W)"
def replace(string, substitutions):

    substrings = sorted(substitutions, key=len, reverse=True)
    print('|'.join(map(apply_white_space, substrings)))
    regex = re.compile('|'.join(map(apply_white_space, substrings)))
    print(lambda match: match.group(0))
    return regex.sub(lambda match: substitutions[match.group(0)], string)

if __name__ == "__main__":
    string = "spam foo bar foo bar spam"
    substitutions = {"foo": "FOO", "bar": "BAR"}
    output = replace(string, substitutions)
    print(output)
