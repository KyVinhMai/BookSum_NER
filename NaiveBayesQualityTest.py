from datasets import load_dataset
import Dataloaders as dl

from datasets import Dataset
from torch.utils.data import DataLoader

import pickle as pkl

import numpy as np
import evaluate

import re

import entity_replacement

from entity_replacement import EntityReplacer
sub_rc = EntityReplacer.sub_random_characters

metric = evaluate.load("accuracy")


import os

def compute_metrics(eval_pred):

    logits, labels = eval_pred

    predictions = np.argmax(logits, axis=-1)

    return metric.compute(predictions=predictions, references=labels)

def my_gen():

    for _ in range(1, 1000):

        num = np.random.choice(np.arange(100))

        yield {"text": "The number is {}. Is it odd?".format(num), "label": num % 2}

def my_tf_sum_gen(files, random_shorten=False, replace_beginning=False):

    for fname in files:

        bp = dl.BookProcessor.init_from_summaries(fname)

        for i in range(len(bp.book_chunk_summaries)):
            if i in bp.failed_summaries:
                continue

            true_sum = bp.book_chunk_summaries[i]
            fake_sum = np.random.choice(bp.false_book_chunk_summaries[i])
            if str(fake_sum) == "None" or not str(fake_sum):
                continue

            if random_shorten:

                newlen = min(len(true_sum), len(fake_sum))
                cut_front = np.random.randint(newlen//5)
                cut_back = np.random.randint(newlen//5)
                true_sum, fake_sum = true_sum[:newlen][cut_front:-cut_back], fake_sum[:newlen][cut_front:-cut_back]

            if replace_beginning:

                true_sum = re.sub("The book extract ", "This book excerpt ", true_sum)
                true_sum = re.sub("The excerpt begins ", "The excerpt starts ", true_sum)

            if np.random.random() < 0.5:
                yield {"text": "Summary 1: {} Summary 2: {}".format(true_sum.strip(), fake_sum.strip()), "label": 0}
            else:
                yield {"text": "Summary 1: {} Summary 2: {}".format(fake_sum.strip(), true_sum.strip()), "label": 1}

def my_tf_sum_gen_simple(files, random_shorten=False, random_one_per_sum=False, replace_beginning=True):

    for fname in files:

        bp = dl.BookProcessor.init_from_summaries(fname)

        for i in range(len(bp.book_chunk_summaries)):
            if i in bp.failed_summaries:
                continue

            true_sum = bp.book_chunk_summaries[i]
            fake_sum = np.random.choice(bp.false_book_chunk_summaries[i])
            if str(fake_sum) == "None" or not str(fake_sum):
                continue

            if random_shorten:
                newlen = min(len(true_sum), len(fake_sum))
                cut_front = np.random.randint(newlen // 5)
                cut_back = np.random.randint(newlen // 5)
                true_sum, fake_sum = true_sum[:newlen][cut_front:-cut_back], fake_sum[:newlen][cut_front:-cut_back]

            if replace_beginning:

                true_sum = re.sub("excerpt", "", true_sum)
                fake_sum = re.sub("excerpt", "", fake_sum)
                #true_sum = re.sub("The excerpt begins ", "The excerpt starts ", true_sum)

            if (random_one_per_sum):
                if np.random.random() < 0.5:
                    yield {"text": "Summary: {}".format(true_sum.strip()), "label": 0}
                else:
                    yield {"text": "Summary: {}".format(fake_sum.strip()), "label": 1}
            else:
                if np.random.random() < 0.5:
                    yield {"text": "Summary: {}".format(true_sum.strip()), "label": 0}
                    yield {"text": "Summary: {}".format(fake_sum.strip()), "label": 1}
                else:
                    yield {"text": "Summary: {}".format(fake_sum.strip()), "label": 1}
                    yield {"text": "Summary: {}".format(true_sum.strip()), "label": 0}


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



# path = os.path.join("Data", "TrainSimplifiedSummaries")
# root, dirs, files = next(os.walk(path))
#
# simplified_sum_files = [os.path.join(root, f) for f in files]

path = os.path.join("Data", "SummaryDataAllMachinesBackupTmpForBert")
root, dirs, files = next(os.walk(path))

all_truefalse_sum_files = [os.path.join(root, f) for f in files]

path = os.path.join("Data", "TrainSimplifiedTF")
root, dirs, files = next(os.walk(path))
simpl_full_files = [os.path.join(root, f) for f in files]

path = os.path.join("Data", "TrainSimplifiedSummaries")
root, dirs, files = next(os.walk(path))
simpl_true_files = [os.path.join(root, f) for f in files]


indices = list(range(1000))
np.random.shuffle(indices) # Have to shuffle here because of a weird batched dataset bug

# dataset_train = Dataset.from_generator(lambda: my_tf_sum_gen_substituted([all_truefalse_sum_files[ind] for ind in indices[0:700]])) # Lambda since it wants a generator function, not a generator object
# dataset_test = Dataset.from_generator(lambda: my_tf_sum_gen_substituted([all_truefalse_sum_files[ind] for ind in indices[700:1000]]))

#dataset_train = Dataset.from_generator(lambda: my_tf_sum_gen_simple_sub([all_truefalse_sum_files[ind] for ind in indices[0:700]])) # Lambda since it wants a generator function, not a generator object
#dataset_test = Dataset.from_generator(lambda: my_tf_sum_gen_simple_sub([all_truefalse_sum_files[ind] for ind in indices[700:1000]]))



dataset_train = Dataset.from_generator(lambda: my_tf_sum_gen_simple([all_truefalse_sum_files[ind] for ind in indices[0:20]] + simpl_true_files, False)) # Lambda since it wants a generator function, not a generator object
#dataset_test = Dataset.from_generator(lambda: my_tf_sum_gen_simple([all_truefalse_sum_files[ind] for ind in indices[700:]], False))
dataset_test = Dataset.from_generator(lambda: my_tf_sum_gen_simple([all_truefalse_sum_files[ind] for ind in indices[700:]], False))



from sklearn.feature_extraction.text import CountVectorizer
count_vector = CountVectorizer()
X_train_counts = count_vector.fit_transform(dataset_train['text'])

from sklearn.feature_extraction.text import TfidfTransformer
tfidf_transformer = TfidfTransformer()

# fit_transform transforms count matrix to tf-idf representation(vector).

X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

from sklearn.naive_bayes import MultinomialNB, BernoulliNB
clf = BernoulliNB(alpha=1).fit(X_train_counts, dataset_train['label'])
#clf = BernoulliNB(alpha=1).fit(X_train_tfidf, dataset_train['label'])
#clf = MultinomialNB().fit(X_train_counts, dataset_train['label'])


## Test

X_new_counts = count_vector.transform(dataset_test['text'])
#X_new_tfidf = tfidf_transformer.transform(X_new_counts)

# Execute prediction(classification).
#predicted = clf.predict(X_new_tfidf)
predicted = clf.predict(X_new_counts)

print(np.mean(predicted == dataset_test["label"]))

import pandas as pd
df_nbf = pd.DataFrame()
df_nbf.index = count_vector.get_feature_names_out()
df_nbf['pos'] = np.e**(clf.feature_log_prob_[0, :])
df_nbf['neg'] = np.e**(clf.feature_log_prob_[1, :])


df_nbf['odds_positive'] = (clf.feature_log_prob_[0, :])/(clf.feature_log_prob_[1, :])

df_nbf['odds_negative'] = (clf.feature_log_prob_[1, :])/(clf.feature_log_prob_[0, :])


odds_false_top15 = df_nbf.sort_values('odds_positive', ascending=False)['odds_positive'][:30]
odds_true_top15 = df_nbf.sort_values('odds_negative', ascending=False)['odds_negative'][:30]

print(odds_false_top15)
print(odds_true_top15)


neg_class_prob_sorted = clf.feature_log_prob_[0, :].argsort()[::-1]
pos_class_prob_sorted = clf.feature_log_prob_[1, :].argsort()[::-1]

print(np.take(count_vector.get_feature_names_out(), neg_class_prob_sorted[:100]))
print(np.take(count_vector.get_feature_names_out(), pos_class_prob_sorted[:100]))

#
# path = os.path.join("Data", "TrainSimplifiedTF")
# #path = os.path.join("Data", "TrainSimplifiedSummaries")
#
# root, dirs, files = next(os.walk(path))
#
# all_simpl_sum_files = [os.path.join(root, f) for f in files]

dataset_test_simpl = Dataset.from_generator(lambda: my_tf_sum_gen_simple(simpl_full_files, False)) # Lamb
X_new_counts = count_vector.transform(dataset_test_simpl['text'])
predicted = clf.predict(X_new_counts)
print(np.mean(predicted == dataset_test_simpl["label"]))