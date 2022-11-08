# Narrative Understanding Dataset
Authors: Arseny Moskvichev, Ky-Vinh Mai

## Introduction

The Narrative Understanding is a  command-line tool for 
generative entity name substitution script made for the **Paper_Name**

Paper link:

## Installation

- spaCy
- tqdm
- gender-guesser

## Usage

NOTE: This script works by placing the substituted summaries within the book folder.

It can NOT work without the original texts, as SpaCy will reference the original
placement of characters in the text in order to replace the string for generating
substitutions or performing modifications.

Original Directory
```angular2html
Corpus Directory
    |
    |__ Websites
            |__Books
                |__Summaries
```

Directory after the script is applied
```angular2html
Corpus Directory
    |
    |__ Website folder
            |__Book folder
                |__Summaries files
                |
                |__Subsituted folder
                          |
                          |__ Character List
                          |
                          |__ Substituted Files
   
```

------------------------------------------------------------------------------------

The file input is json or text and will output the same filetype as the input type.
```angular2html
python entity_replacement.py [--all or --book or --file] [input_file_path]
```
 # Input File Format

The Character list must be in a JSON file format.

Uses gendered names from https://archive.ics.uci.edu/ml/datasets/Gender+by+Name
Uses Unisex names from https://fivethirtyeight.datasettes.com/fivethirtyeight/unisex-names~2Funisex_names_table
