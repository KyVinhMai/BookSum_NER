def read_gender_list(gender_file) -> tuple[list,list]:
    male_names = []
    female_names = []
    with open(gender_file, "r")  as f:
        for line in f:
            if line.rstrip("\n").split(",")[1] == "M": #Checks if the name is male
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