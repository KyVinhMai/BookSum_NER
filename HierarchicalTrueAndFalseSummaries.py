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
import pickle as pkl

from settings import column_separator, fake_summary_separator, line_separator

from gpt_api_processing import SummarizeSummaries

def load_processors_and_dicts(summary_folder, ent_dict_folder, num_to_process=15, start_at=0):
    sumpath = os.path.join("Data", summary_folder)
    entpath = os.path.join("Data", ent_dict_folder)

    bookf_to_process = [f.strip(".tagseparated") for f in os.listdir(sumpath) if os.path.isfile(os.path.join(sumpath, f))]
    bookf_to_process = bookf_to_process[start_at:num_to_process]

    summaries_to_process = [os.path.join(sumpath, f + ".tagseparated") for f in bookf_to_process]
    ent_dicts_to_process = [os.path.join(entpath, f + ".repl") for f in bookf_to_process]

    assert all([os.path.isfile(f) for f in ent_dicts_to_process]), 'Missing a preprocessed replacement dictionary {}'.format(ent_dicts_to_process)

    book_processors = [dl.BookProcessor.init_from_summaries(s) for s in summaries_to_process]

    ent_rep_dicts = []

    for p in ent_dicts_to_process:
        with open(p, "rb") as f:
            ent_rep_dicts.append(pkl.load(f))

    return book_processors, ent_rep_dicts

def get_true_hierarchical_summaries(bp):

    true_summaries = bp.book_chunk_summaries
    false_summaries_filtered = [[s for s in fs if s] for fs in bp.false_book_chunk_summaries]

    false_summaries = [np.random.choice(b) if len(b) >= 1 else None for b in false_summaries_filtered]

    assert len(true_summaries) == len(false_summaries), "True and false raw summaries lengths differ!"


    cur_level = 0
    levels = [cur_level for _ in range(len(true_summaries))]

    current_meta_summaries = true_summaries.copy()

    for level in range(1, 25):

        if len(current_meta_summaries) == 1:
            break

        new_meta_summaries = SummarizeSummaries(current_meta_summaries)

        true_summaries.extend(new_meta_summaries)
        false_summaries.extend(["None" for _ in range(len(new_meta_summaries))])
        levels.extend([level for _ in range(len(new_meta_summaries))])

        current_meta_summaries = new_meta_summaries.copy()

        print("Created hierarchical summaries level {}".format(level))
        print(current_meta_summaries[0:5])
        print(len(current_meta_summaries))

    return true_summaries, false_summaries, levels





if __name__ == "__main__":

    bp, ent_dicts = load_processors_and_dicts("SummaryDataAllMachines", "CharacterSubstitutionBackup")

    true_summaries, false_summaries, levels = get_true_hierarchical_summaries(bp[0])

    # Save hierarchical chunks here


