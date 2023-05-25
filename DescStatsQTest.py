from datasets import load_dataset
from transformers import AutoTokenizer
import Dataloaders as dl

from datasets import Dataset
from torch.utils.data import DataLoader

import pickle as pkl

import numpy as np
import evaluate

import entity_replacement

from entity_replacement import EntityReplacer
sub_rc = EntityReplacer.sub_random_characters

metric = evaluate.load("accuracy")

import torch as t
device = t.device("cuda") if t.cuda.is_available() else t.device("cpu")

import os

def compute_metrics(eval_pred):

    logits, labels = eval_pred

    predictions = np.argmax(logits, axis=-1)

    return metric.compute(predictions=predictions, references=labels)

def my_gen():

    for _ in range(1, 1000):

        num = np.random.choice(np.arange(100))

        yield {"text": "The number is {}. Is it odd?".format(num), "label": num % 2}

def my_tf_sum_gen(files):

    for fname in files:

        bp = dl.BookProcessor.init_from_summaries(fname)

        for i in range(len(bp.book_chunk_summaries)):
            if i in bp.failed_summaries:
                continue

            true_sum = bp.book_chunk_summaries[i]
            fake_sum = np.random.choice(bp.false_book_chunk_summaries[i])
            if str(fake_sum) == "None" or not str(fake_sum):
                continue


            if np.random.random() < 0.5:
                yield {"text": "Summary 1: {} Summary 2: {}".format(true_sum.strip(), fake_sum.strip()), "label": 0}
            else:
                yield {"text": "Summary 1: {} Summary 2: {}".format(fake_sum.strip(), true_sum.strip()), "label": 1}

def my_tf_sum_gen_simple(files):

    for fname in files:

        bp = dl.BookProcessor.init_from_summaries(fname)

        for i in range(len(bp.book_chunk_summaries)):
            if i in bp.failed_summaries:
                continue

            true_sum = bp.book_chunk_summaries[i]
            fake_sum = np.random.choice(bp.false_book_chunk_summaries[i])
            if str(fake_sum) == "None" or not str(fake_sum):
                continue


            yield {"text": "Summary: {}".format(true_sum.strip()), "label": 0}
            yield {"text": "Summary: {}".format(fake_sum.strip()), "label": 1}

def my_tf_sum_gen_simple_sub(files):

    for fname in files:

        bp = dl.BookProcessor.init_from_summaries(fname)
        bname = fname.split("/")[-1].split(".tagseparated")[-2]

        ent_dict_p = os.path.join("Data", "CharacterSubstitutionBackup", bname + ".repl")
        with open(ent_dict_p, "rb") as f:
            ent_dict = pkl.load(f)

        for i in range(len(bp.book_chunk_summaries)):
            if i in bp.failed_summaries:
                continue

            true_sum = sub_rc(ent_dict, bp.book_chunk_summaries[i])
            fake_sum = np.random.choice(bp.false_book_chunk_summaries[i])
            if str(fake_sum) == "None" or not str(fake_sum):
                continue

            fake_sum = sub_rc(ent_dict, fake_sum)

            yield {"text": "Summary: {}".format(true_sum.strip()), "label": 0}
            yield {"text": "Summary: {}".format(fake_sum.strip()), "label": 1}


def my_tf_sum_gen_substituted(files):

    for fname in files:

        bp = dl.BookProcessor.init_from_summaries(fname)
        bname = fname.split("/")[-1].split(".tagseparated")[-2]

        ent_dict_p = os.path.join("Data", "CharacterSubstitutionBackup", bname + ".repl")
        with open(ent_dict_p, "rb") as f:
            ent_dict = pkl.load(f)


        for i in range(len(bp.book_chunk_summaries)):
            if i in bp.failed_summaries:
                continue

            true_sum = sub_rc(ent_dict, bp.book_chunk_summaries[i])
            fake_sum = np.random.choice(bp.false_book_chunk_summaries[i])
            if str(fake_sum) == "None" or not str(fake_sum):
                continue

            fake_sum = sub_rc(ent_dict, fake_sum)



            if np.random.random() < 0.5:
                yield {"text": "Summary 1: {} Summary 2: {}".format(true_sum.strip(), fake_sum.strip()), "label": 0}
            else:
                yield {"text": "Summary 1: {} Summary 2: {}".format(fake_sum.strip(), true_sum.strip()), "label": 1}



path = os.path.join("Data", "SummaryDataAllMachinesBackupTmpForBert")
root, dirs, files = next(os.walk(path))

all_truefalse_sum_files = [os.path.join(root, f) for f in files]
#

all_truefalse_sums = list(my_tf_sum_gen_simple(all_truefalse_sum_files))


true_lens = []
false_lens = []

for i, el in enumerate(all_truefalse_sums):
    if el["label"] == 0:
        true_lens.append(len(el["text"].split()))
    else:
        false_lens.append(len(el["text"].split()))

print("Mean true {}, Mean false {}, Median true {}, Median false ()")

true_larger = []
for t, f in zip(true_lens, false_lens):
    if t > f:
        true_larger.append(1)
    else:
        true_larger.append(0)

print("True is larger in {} of cases".format(np.mean(true_larger)))