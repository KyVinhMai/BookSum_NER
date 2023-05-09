from datasets import load_dataset
from transformers import AutoTokenizer


from datasets import Dataset

import numpy as np
import evaluate
metric = evaluate.load("accuracy")

import torch as t
device = t.device("cuda") if t.cuda.is_available() else t.device("cpu")

def compute_metrics(eval_pred):

    logits, labels = eval_pred

    predictions = np.argmax(logits, axis=-1)

    return metric.compute(predictions=predictions, references=labels)

def my_gen():

    for _ in range(1, 1000):

        num = np.random.choice(np.arange(100))

        yield {"text": "The number is {}. Is it odd?".format(num), "label": num % 2}


dataset = Dataset.from_generator(my_gen)

tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

def tokenize_function(examples):

    return tokenizer(examples["text"], padding="max_length", truncation=True)

tokenized_datasets = dataset.map(tokenize_function, batched=True)

from transformers import AutoModelForSequenceClassification
model = AutoModelForSequenceClassification.from_pretrained("bert-base-cased", num_labels=2)

from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(output_dir="test_evenness_trainer", evaluation_strategy="epoch")


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
tokenized_datasets = tokenized_datasets.remove_columns(["text"])
tokenized_datasets = tokenized_datasets.rename_column("label", "labels")
tokenized_datasets.set_format("torch")


from torch.utils.data import DataLoader
train_dataloader = DataLoader(tokenized_datasets, shuffle=True, batch_size=24)
eval_dataloader = DataLoader(tokenized_datasets, batch_size=24)

from torch.optim import AdamW
optimizer = AdamW(model.parameters(), lr=5e-5)

from transformers import get_scheduler
num_epochs = 3
num_training_steps = num_epochs * len(train_dataloader)

lr_scheduler = get_scheduler(name="linear", optimizer=optimizer, num_warmup_steps=0, num_training_steps=num_training_steps)

from tqdm.auto import tqdm
progress_bar = tqdm(range(num_training_steps))
model.train()



for epoch in range(num_epochs):

    for batch in train_dataloader:

        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()
        progress_bar.update(1)

metric = evaluate.load("accuracy")

model.eval()
for batch in eval_dataloader:

    batch = {k: v.to(device) for k, v in batch.items()}

    with t.no_grad():

        outputs = model(**batch)

    logits = outputs.logits
    predictions = t.argmax(logits, dim=-1)
    metric.add_batch(predictions=predictions, references=batch["labels"])

res = metric.compute()