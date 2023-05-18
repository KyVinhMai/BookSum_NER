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

import json

summary_folder = "TrueAndFalseSummaryDataBackup"

sumpath = os.path.join("Data", summary_folder)

bookf_to_process = [f.strip(".tagseparated") for f in os.listdir(sumpath) if os.path.isfile(os.path.join(sumpath, f))]
summaries_to_process = [os.path.join(sumpath, f + ".tagseparated") for f in bookf_to_process]

#assert all([os.path.isfile(f) for f in ent_dicts_to_process]), 'Missing a preprocessed replacement dictionary {}'.format(ent_dicts_to_process)

book_processors = [dl.BookProcessor.init_from_summaries(s) for s in summaries_to_process]

np.random.shuffle(book_processors)

finalpath = os.path.join("Data", "true_vs_false_10_batches_of_10.json")

res = {}

for i in range(10):
    res[i] = []
    for j in range(10):

        while True:

            bp = book_processors.pop()
            sum_ind = np.random.randint(len(bp.overlapped_book_chunks))
            if sum_ind in bp.failed_summaries:
                continue
            else:
                snippet = bp.overlapped_book_chunks[sum_ind]
                if len(snippet) > 3600 or len(snippet) < 1000:
                    continue

                true_sum = bp.book_chunk_summaries[sum_ind]
                fake_sum = np.random.choice(bp.false_book_chunk_summaries[sum_ind])

                if true_sum and str(true_sum) != "None" and str(fake_sum) != "None":
                    res[i].append({"true_sum": true_sum, "fake_sum": fake_sum, "snippet": snippet})
                    break


with open(finalpath, "w") as f:
    json.dump(res, f)




