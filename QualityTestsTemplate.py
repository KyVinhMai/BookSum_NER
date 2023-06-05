from datasets import load_dataset
from transformers import AutoTokenizer
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

def my_tf_sum_gen_simple(files, random_shorten=False, random_one_per_sum=False):

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



path = os.path.join("Data", "TrainSimplifiedSummaries")
root, dirs, files = next(os.walk(path))

simplified_sum_files = [os.path.join(root, f) for f in files]

path = os.path.join("Data", "SummaryDataAllMachinesBackupTmpForBert")
root, dirs, files = next(os.walk(path))

all_truefalse_sum_files = [os.path.join(root, f) for f in files]
#
# dataset_train = Dataset.from_generator(lambda: my_tf_sum_gen(all_truefalse_sum_files[0:700])) # Lambda since it wants a generator function, not a generator object
# dataset_test = Dataset.from_generator(lambda: my_tf_sum_gen(all_truefalse_sum_files[700:]))

#
# dataset_train = Dataset.from_generator(lambda: my_tf_sum_gen(all_truefalse_sum_files[0:100])) # Lambda since it wants a generator function, not a generator object
# dataset_test = Dataset.from_generator(lambda: my_tf_sum_gen(all_truefalse_sum_files[100:125]))

indices = list(range(1000))
np.random.shuffle(indices) # Have to shuffle here because of a weird batched dataset bug

# dataset_train = Dataset.from_generator(lambda: my_tf_sum_gen_substituted([all_truefalse_sum_files[ind] for ind in indices[0:700]])) # Lambda since it wants a generator function, not a generator object
# dataset_test = Dataset.from_generator(lambda: my_tf_sum_gen_substituted([all_truefalse_sum_files[ind] for ind in indices[700:1000]]))

#dataset_train = Dataset.from_generator(lambda: my_tf_sum_gen_simple_sub([all_truefalse_sum_files[ind] for ind in indices[0:700]])) # Lambda since it wants a generator function, not a generator object
#dataset_test = Dataset.from_generator(lambda: my_tf_sum_gen_simple_sub([all_truefalse_sum_files[ind] for ind in indices[700:1000]]))


dataset_train = Dataset.from_generator(lambda: my_tf_sum_gen([all_truefalse_sum_files[ind] for ind in indices[0:200]] + simplified_sum_files[0:15], False)) # Lambda since it wants a generator function, not a generator object
dataset_test = Dataset.from_generator(lambda: my_tf_sum_gen([all_truefalse_sum_files[ind] for ind in indices[200:250]], False))

#dataset_train = Dataset.from_generator(lambda: my_tf_sum_gen_simple([all_truefalse_sum_files[ind] for ind in indices[0:200]], False)) # Lambda since it wants a generator function, not a generator object
#dataset_test = Dataset.from_generator(lambda: my_tf_sum_gen_simple([all_truefalse_sum_files[ind] for ind in indices[200:250]], False))

tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

def tokenize_function(examples):

    return tokenizer(examples["text"], padding="max_length", truncation=True)

tokenized_dataset_train = dataset_train.map(tokenize_function, batched=True)
tokenized_dataset_test = dataset_test.map(tokenize_function, batched=True)

from transformers import AutoModelForSequenceClassification
model = AutoModelForSequenceClassification.from_pretrained("bert-base-cased", num_labels=2)

from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(output_dir="test_fakedetector_trainer", evaluation_strategy="epoch")


model.to(device)

# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=tokenized_datasets,
#     eval_dataset=tokenized_datasets,
#     compute_metrics=compute_metrics,
#
# )
#
# trainer.train()


# Trying to train with pytorch instead
tokenized_dataset_train = tokenized_dataset_train.remove_columns(["text"])
tokenized_dataset_train = tokenized_dataset_train.rename_column("label", "labels")
tokenized_dataset_train.set_format("torch")

tokenized_dataset_test = tokenized_dataset_test.remove_columns(["text"])
tokenized_dataset_test = tokenized_dataset_test.rename_column("label", "labels")
tokenized_dataset_test.set_format("torch")






train_dataloader = DataLoader(tokenized_dataset_train, shuffle=False, batch_size=24)
eval_dataloader = DataLoader(tokenized_dataset_test, batch_size=24)

from torch.optim import AdamW
optimizer = AdamW(model.parameters(), lr=5e-5)

from transformers import get_scheduler
num_epochs = 3
num_training_steps = num_epochs * len(train_dataloader)

lr_scheduler = get_scheduler(name="linear", optimizer=optimizer, num_warmup_steps=0, num_training_steps=num_training_steps)

from tqdm.auto import tqdm
progress_bar = tqdm(range(num_training_steps))



metric = evaluate.load("accuracy")

accuracies = []

for epoch in range(num_epochs):

    model.train()

    for batch in train_dataloader:

        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()
        progress_bar.update(1)

    model.eval()
    for batch in eval_dataloader:
        batch = {k: v.to(device) for k, v in batch.items()}

        with t.no_grad():
            outputs = model(**batch)

        logits = outputs.logits
        predictions = t.argmax(logits, dim=-1)
        metric.add_batch(predictions=predictions, references=batch["labels"])


    accuracies.append(metric.compute())
    print("Accuracy: {}".format(accuracies[-1]))
    
    


def my_diagnostic_dataset():
    true_sum = "The excerpt describes Adela and Arabella’s different experiences during the yachting excursions. Adela is having a great time and writes to Arabella about the fun they are having. Arabella, on the other hand, is miserable and writes to Adela about the mundane daily events at Brookfield. The Hon. Mrs. Bayruffle accompanies the ladies on the yacht and Adela admires her social skills but realizes that society is not everything. The excerpt also touches on the idea that when people experience a great fall, they rarely indulge in melancholy until they can take it as a luxury."
    defancy_true = "The passage talks about how Adela and Arabella have different experiences while they are out on the yachting trip. Adela has a wonderful time and tells Arabella about all of the enjoyable things they are doing. Meanwhile, Arabella is unhappy and writes to Adela about the routine events happening at Brookfield. The Hon. Mrs. Bayruffle comes with them on the yacht and Adela likes how well she gets along with everyone, but she realizes that being a part of high society isn't the only important thing. The passage also touches on the idea that when people suffer a great loss, they don't usually feel sad until they have the luxury of time to reflect on it."
    fake = "The excerpt describes two friends, Adela and Arabella, taking a walk in the countryside. Adela is awestruck by the natural beauty around them and tells Arabella about the great time they are having. Arabella, however, is unimpressed and complains to Adela about the lack of proper civilization out here. The Hon. Mrs. Bayruffle joins the ladies for the walk and Adela learns a valuable lesson about the importance of solitude. The excerpt also touches on the idea that adversity reveals the true strength of a person's character."
    data = [{"text": "Summary 1: {} Summary 2: {}".format(true_sum, defancy_true), "label": 0},
            {"text": "Summary 1: {} Summary 2: {}".format(defancy_true, true_sum), "label": 1},
            {"text": "Summary 1: {} Summary 2: {}".format(defancy_true, fake), "label": 1},
            {"text": "Summary 1: {} Summary 2: {}".format(fake, defancy_true), "label": 0},
            {"text": "Summary 1: {} Summary 2: {}".format(fake, true_sum), "label": 1}]

    for d in data:
        yield d

def my_diagnostic_dataset_single():
    true_sum = "The excerpt describes Adela and Arabella’s different experiences during the yachting excursions. Adela is having a great time and writes to Arabella about the fun they are having. Arabella, on the other hand, is miserable and writes to Adela about the mundane daily events at Brookfield. The Hon. Mrs. Bayruffle accompanies the ladies on the yacht and Adela admires her social skills but realizes that society is not everything. The excerpt also touches on the idea that when people experience a great fall, they rarely indulge in melancholy until they can take it as a luxury."
    defancy_true = "The passage talks about how Adela and Arabella have different experiences while they are out on the yachting trip. Adela has a wonderful time and tells Arabella about all of the enjoyable things they are doing. Meanwhile, Arabella is unhappy and writes to Adela about the routine events happening at Brookfield. The Hon. Mrs. Bayruffle comes with them on the yacht and Adela likes how well she gets along with everyone, but she realizes that being a part of high society isn't the only important thing. The passage also touches on the idea that when people suffer a great loss, they don't usually feel sad until they have the luxury of time to reflect on it."
    fake = "The excerpt describes two friends, Adela and Arabella, taking a walk in the countryside. Adela is awestruck by the natural beauty around them and tells Arabella about the great time they are having. Arabella, however, is unimpressed and complains to Adela about the lack of proper civilization out here. The Hon. Mrs. Bayruffle joins the ladies for the walk and Adela learns a valuable lesson about the importance of solitude. The excerpt also touches on the idea that adversity reveals the true strength of a person's character."
    data = [{"text": "Summary: {}".format(true_sum), "label": 0},
            {"text": "Summary: {}".format(defancy_true), "label": 0},
            {"text": "Summary: {}".format(fake), "label": 1}]

    for d in data:
        yield d

dataset_diag = Dataset.from_generator(my_diagnostic_dataset)
#dataset_diag = Dataset.from_generator(my_diagnostic_dataset_single)
tokenized_dataset_diag = dataset_diag.map(tokenize_function, batched=True)


tokenized_dataset_diag = tokenized_dataset_diag.remove_columns(["text"])
tokenized_dataset_diag = tokenized_dataset_diag.rename_column("label", "labels")
tokenized_dataset_diag.set_format("torch")

model.eval()

diag_dataloader = DataLoader(tokenized_dataset_diag, batch_size=24)
for batch in diag_dataloader:
    batch = {k: v.to(device) for k, v in batch.items()}

    with t.no_grad():
        outputs = model(**batch)

    logits = outputs.logits
    predictions = t.argmax(logits, dim=-1)
    print(predictions)
    metric.add_batch(predictions=predictions, references=batch["labels"])


### diagnostic on the simplified dataset



path = os.path.join("Data", "TrainSimplifiedTF")
#path = os.path.join("Data", "TrainSimplifiedSummaries")
root, dirs, files = next(os.walk(path))

simplified_sum_files = [os.path.join(root, f) for f in files]


#dataset_diag = Dataset.from_generator(lambda: my_tf_sum_gen_simple(simplified_sum_files[-8:], random_shorten=False, random_one_per_sum=True)) # Lambda since it wants a generator function, not a generator objectmy_tf_sum_gen_simple
dataset_diag = Dataset.from_generator(lambda: my_tf_sum_gen(simplified_sum_files)) # Lambda since it wants a generator function, not a generator objectmy_tf_sum_gen_simple
#dataset_diag = Dataset.from_generator(lambda: my_tf_sum_gen(simplified_sum_files)) # Lambda since it wants a generator function, not a generator objectmy_tf_sum_gen_simple



tokenized_dataset_diag = dataset_diag.map(tokenize_function, batched=True)
tokenized_dataset_diag = tokenized_dataset_diag.remove_columns(["text"])
tokenized_dataset_diag = tokenized_dataset_diag.rename_column("label", "labels")
tokenized_dataset_diag.set_format("torch")

model.eval()

metric = evaluate.load("accuracy")

diag_dataloader = DataLoader(tokenized_dataset_diag, batch_size=24)
for batch in diag_dataloader:
    batch = {k: v.to(device) for k, v in batch.items()}

    with t.no_grad():
        outputs = model(**batch)

    logits = outputs.logits
    predictions = t.argmax(logits, dim=-1)
    #print(predictions)
    metric.add_batch(predictions=predictions, references=batch["labels"])

#accuracies.append(metric.compute())
print("Accuracy: {}".format(metric.compute()))


## Acc on a small simplified subset: 0.685