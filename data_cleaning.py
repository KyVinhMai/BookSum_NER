from __future__ import annotations
import argparse
from pathlib import Path
from tqdm import tqdm

def parse_summaries(book: Path):
    "For each summary create the file path for it"
    for entry in book.iterdir():
        if entry.is_dir():
            for summaries in entry.iterdir():
                if "-1" in summaries.stem:
                    summaries.unlink()

def parse_corpus(corpus_path) -> None:
    "Parses through each website directory, and then in each book folder in the dataset, create the folder for subsituted books"

    for website in corpus_path.iterdir(): #i.e. Shmoop, Sparknotes
        for book in tqdm(website.iterdir(), desc = "Books list", unit = "Amount of books"): # i.e. Hamlet, Frankenstein
            parse_summaries(book)


parse_corpus(Path("D:\\Users\\kyvin.DESKTOP-ERBCV8T\\PycharmProjects\\Research-projects\\book_dataset\\booksum\\scripts\\finished_summaries"))