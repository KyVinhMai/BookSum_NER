import re
import textwrap
import copy
import spacy
import spacy_transformers
nlp = spacy.load('en_core_web_trf')

text = ("Alexander the Great once said that a man musn't fight unless needed")


doc = nlp(text)

print(doc.ents)