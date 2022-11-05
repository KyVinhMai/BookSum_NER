
file = ("D:\\Users\\kyvin.DESKTOP-ERBCV8T\\PycharmProjects\\Research-projects\\book_dataset\\booksum\\scripts\\finished_summaries\\bookwolf\\A Tale of Two Cities\\ATaleofTwoCities_substituted\\ATaleofTwoCities_character_list.txt")

with open(file, "r") as f: #todo why couldn't we initialize self.char_list with a function?
    universal_character_list = (f.read())
    _, lcl = universal_character_list.split("\n\n\n")
    print(eval(lcl))

# char_list = []
# with open("name_exceptions.txt", "r") as f:
#     for line in f:
#         char_list.append(line.rstrip())
#
# print(char_list)