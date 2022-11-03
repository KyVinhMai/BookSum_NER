# BookSum_NER
Authors: Arseny Moskvichev, Ky-Vinh Mai

## Introduction

**Paper_Name** is a  command-line tool for 
generative entity name substitution script made for the **Paper_Name**

Paper link:

## Installation

- spaCy
- tqdm
- gender-guesser

## Usage

NOTE: This script works by placing the substituted summaries within the book folder.

It CANNOT work without the original texts, as SpaCy will reference the original
placement of characters in the text in order to replace the string for generating
substitutions or performing modifications.
------------------------------------------------------------------------------------
```angular2html
python entity_replacement.py -r [input_file_path]  [input_type]
```
 # Input File Format

The Character list must be in a JSON file format.

Uses gendered names from https://archive.ics.uci.edu/ml/datasets/Gender+by+Name
Uses Unisex names from https://fivethirtyeight.datasettes.com/fivethirtyeight/unisex-names~2Funisex_names_table
