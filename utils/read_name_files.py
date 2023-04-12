def read_gender_list() -> tuple[list,list]:
    male_names = []
    female_names = []
    with open("NameDatasets/name_gender_dataset.csv", "r")  as f:
        for line in f:
            if line.rstrip("\n").split(",")[1] == "M": #Checks if the name is male
                male_names.append(line.rstrip("\n").split(",")[0])
            else:
                female_names.append(line.rstrip("\n").split(",")[0])

    return male_names, female_names

def read_unisex_names() -> list:
    uni_names = []
    with open("NameDatasets/unisex-names~2Funisex_names_table.csv", "r")  as f:
        for line in f:
            uni_names.append(line.rstrip("\n").split(",")[2])

    return uni_names

def read_exceptions() -> list:
    name_exceptions = []
    with open("NameDatasets/name_exceptions.txt", "r") as f:
        for line in f:
            name_exceptions.append(line.rstrip())

    return name_exceptions

def read_figures() -> list:
    celebrities = []
    with open("NameDatasets/historical_figures", "r") as f:
        for line in f:
            celebrities.append(line.rstrip())

    return celebrities