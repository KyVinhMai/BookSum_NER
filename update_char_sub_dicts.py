import pickle as pkl
import os

### Takes all Character Substitution dictionaries and removes exception names from them.

if __name__ == "__main__":

    path = os.path.join("Data", "CharacterSubstitution")
    from utils.read_name_files import read_exceptions


    EXCEPTIONS = read_exceptions()

    for root, dirs, files in os.walk(path, topdown=False):
       for name in files:
       # for name in dirs:
       #    print(os.path.join(root, name))

          with open(os.path.join(root, name), "rb") as f:
              res = pkl.load(f)

              if res["Table_Type"] == "Character Counts":
                  for ex in EXCEPTIONS:
                      if ex in res["Characters"]:
                          del res["Characters"][ex]
                          print("Deleted exception name {} from character counts".format(ex))


              elif res["Table_Type"] == "Randomized Names":
                  for ex in EXCEPTIONS:
                      for nametype in ["First Names", "Middle Names", "Last Names"]:
                          if ex in res[nametype]:
                              del res[nametype][ex]
                              print("Deleted exception name {} from randomized names".format(ex))

              else:
                  raise ValueError("Unknown table type {}".format(res['TableType']))

          with open(os.path.join(root, name), "wb") as f:
              pkl.dump(res, f)