import pickle as pkl

import random

import warnings

import os

import Dataloaders as dl
import settings

import numpy as np
random.seed(42)
np.random.seed(42)

from collections import Counter

from entity_replacement import EntityReplacer

import character_list_generator as clg


if __name__ == "__main__":

    results_folder = "CharacterSubstitution" # Where to save char sub dicts
    sum_folder = "TrueAndFalseSummaryDataBackup" # Where to look for processed books


    respath = os.path.join("Data", results_folder)

    done = set([f.split('.')[0] for f in os.listdir(respath) if os.path.isfile(os.path.join(respath, f))])

    sumpath = os.path.join("Data", sum_folder)

    sums_to_process = [f for f in os.listdir(sumpath) if os.path.isfile(os.path.join(sumpath, f)) and f.strip(".tagseparated") not in done]

    for i, f in enumerate(sums_to_process):

        print("Beginning to process book {}/{}".format(i + 1, len(sums_to_process)))

        sp = os.path.join(sumpath, f)

        b = dl.BookProcessor.init_from_summaries(sp)
        ent_count, ent_rep_dict = clg.get_counts_and_subs(b.original_book_text)

        resname = f.strip(".tagseparated")
        rp = os.path.join(respath, resname)
        with open(rp + ".count", "wb") as o:
            pkl.dump(ent_count, o)

        with open(rp + ".repl", "wb") as o:
            pkl.dump(ent_rep_dict, o)
