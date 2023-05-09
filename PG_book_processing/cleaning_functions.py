
# -*- coding: utf-8 -*-
"""Adapted from https://github.com/pgcorpus/gutenberg/blob/master/src/cleanup.py
    which, in turn, is adapted from https://github.com/c-w/gutenberg/."""

from __future__ import unicode_literals
import os
import io
import re

def clean_read(path: str): #-> tuple[str,str,str]:
    """
    Remove headers from raw txt file.
    Parameters
    ----------
    path : string - Path to the PG****_raw.txt file
    return: Author name, title, and cleaned book text
    """

    import os
    # print(os.path.dirname(os.path.realpath(__file__)))

    with io.open(path, encoding="latin-1") as f:
        text = f.read()

    author, title = get_metadata(text)
    clean = strip_headers(text)
    clean = rm_title_author(author, title, clean)

    return author, title, clean

############

def create_pattern(title: str, author: str):
    """
    Attempt at a regular expression
    (HAPPINESS|(h|H)appiness)(\s+|\n+)(AND|(a|A)nd)(\s+|\n+)(MARRIAGE|(m|M)arriage)(\s+|\n+)(By|BY|by)(\s{1,3}|\n{1,3})(ELIZABETH|Elizabeth) (TOWNE|Towne)
    """
    title_words = [(word.upper(), word) for word in title.split(" ")]
    author_words = [(word.upper(), word) for word in author.split(" ")]
    title_pattern = "".join([f"({pair[0]}|({pair[1][0].lower()}|{pair[1][0].upper()}){pair[1][1:]})(\s+|\n+)" for pair in title_words])
    author_pattern = " ".join([f"({pair[0]}|({pair[1][0].lower()}|{pair[1][0].upper()}){pair[1][1:]})" for pair in author_words])
    pattern = title_pattern + "(By|BY|by)(\s{1,3}|\n{1,3})" + author_pattern

    return pattern

def rm_title_author(author:str, title:str, clean:str) -> str:
    "Author, title"
    try:
        pattern1 = create_pattern(title, author)
        clean = re.sub(pattern1, "", clean)
    except Exception as e:
        pass

    return clean


TEXT_START_MARKERS = frozenset((
    "*END*THE SMALL PRINT",
    "*** START OF THE PROJECT GUTENBERG",
    "*** START OF THIS PROJECT GUTENBERG",
    "This etext was prepared by",
    "E-text prepared by",
    "Produced by",
    "Distributed Proofreading Team",
    "Proofreading Team at http://www.pgdp.net",
    "http://gallica.bnf.fr)",
    "      http://archive.org/details/",
    "http://www.pgdp.net",
    "by The Internet Archive)",
    "by The Internet Archive/Canadian Libraries",
    "by The Internet Archive/American Libraries",
    "public domain material from the Internet Archive",
    "Internet Archive)",
    "Internet Archive/Canadian Libraries",
    "Internet Archive/American Libraries",
    "material from the Google Print project",
    "*END THE SMALL PRINT",
    "***START OF THE PROJECT GUTENBERG",
    "This etext was produced by",
    "*** START OF THE COPYRIGHTED",
    "The Project Gutenberg",
    "http://gutenberg.spiegel.de/ erreichbar.",
    "Project Runeberg publishes",
    "Beginning of this Project Gutenberg",
    "Project Gutenberg Online Distributed",
    "Gutenberg Online Distributed",
    "the Project Gutenberg Online Distributed",
    "Project Gutenberg TEI",
    "This eBook was prepared by",
    "http://gutenberg2000.de erreichbar.",
    "This Etext was prepared by",
    "This Project Gutenberg Etext was prepared by",
    "Gutenberg Distributed Proofreaders",
    "Project Gutenberg Distributed Proofreaders",
    "the Project Gutenberg Online Distributed Proofreading Team",
    "**The Project Gutenberg",
    "*SMALL PRINT!",
    "More information about this book is at the top of this file.",
    "tells you about restrictions in how the file may be used.",
    "l'authorization à les utilizer pour preparer ce texte.",
    "of the etext through OCR.",
    "*****These eBooks Were Prepared By Thousands of Volunteers!*****",
    "We need your donations more than ever!",
    " *** START OF THIS PROJECT GUTENBERG",
    "****     SMALL PRINT!",
    '["Small Print" V.',
    '      (http://www.ibiblio.org/gutenberg/',
    'and the Project Gutenberg Online Distributed Proofreading Team',
    'Mary Meehan, and the Project Gutenberg Online Distributed Proofreading',
    '                this Project Gutenberg edition.',
))


TEXT_END_MARKERS = frozenset((
    "*** END OF THE PROJECT GUTENBERG",
    "*** END OF THIS PROJECT GUTENBERG",
    "***END OF THE PROJECT GUTENBERG",
    "End of the Project Gutenberg",
    "End of The Project Gutenberg",
    "Ende dieses Project Gutenberg",
    "by Project Gutenberg",
    "End of Project Gutenberg",
    "End of this Project Gutenberg",
    "Ende dieses Projekt Gutenberg",
    "        ***END OF THE PROJECT GUTENBERG",
    "*** END OF THE COPYRIGHTED",
    "End of this is COPYRIGHTED",
    "Ende dieses Etextes ",
    "Ende dieses Project Gutenber",
    "Ende diese Project Gutenberg",
    "**This is a COPYRIGHTED Project Gutenberg Etext, Details Above**",
    "Fin de Project Gutenberg",
    "The Project Gutenberg Etext of ",
    "Ce document fut presente en lecture",
    "Ce document fut présenté en lecture",
    "More information about this book is at the top of this file.",
    "We need your donations more than ever!",
    "END OF PROJECT GUTENBERG",
    " End of the Project Gutenberg",
    " *** END OF THIS PROJECT GUTENBERG",
))


LEGALESE_START_MARKERS = frozenset(("<<THIS ELECTRONIC VERSION OF",))
LEGALESE_END_MARKERS = frozenset(("SERVICE THAT CHARGES FOR DOWNLOAD",))

def read_book_safe(path, error_handling=None):

    for e in ["utf-8", "cp1252", "latin-1"]:

        try:

            with open(path, "r", encoding=e, errors=error_handling) as book:
                text = book.read()

            return text

        except Exception:

            continue

    raise ValueError

def get_metadata(text):
    author = ""
    title = ""
    lines = text.splitlines()
    sep = str(os.linesep)

    out = []
    i = 0
    footer_found = False
    ignore_section = False

    for i, line in enumerate(lines):
        reset = False

        if i <= 600:
            # Check if the header ends here
            if line.startswith("Author:"):
                author = line[7:].strip()

            if line.startswith("Title:"):
                title = line[6:].strip()

        else:
            break

    return author, title

def strip_headers(text):
    """
    Remove lines that are part of the Project Gutenberg header or footer.
    Note: this function is a port of the C++ utility by Johannes Krugel. The
    original version of the code can be found at:
    http://www14.in.tum.de/spp1307/src/strip_headers.cpp
    Args:
        text (unicode): The body of the text to clean up.
    Returns:
        unicode: The text with any non-text content removed.
    """
    lines = text.splitlines()
    sep = str(os.linesep)

    out = []
    i = 0
    footer_found = False
    ignore_section = False

    for line in lines:
        reset = False

        if i <= 600:
            # Check if the header ends here
            if any(line.startswith(token) for token in TEXT_START_MARKERS):
                reset = True

            # If it's the end of the header, delete the output produced so far.
            # May be done several times, if multiple lines occur indicating the
            # end of the header
            if reset:
                out = []
                continue

        if i >= 100:
            # Check if the footer begins here
            if any(line.startswith(token) for token in TEXT_END_MARKERS):
                footer_found = True

            # If it's the beginning of the footer, stop output
            if footer_found:
                break

        if any(line.startswith(token) for token in LEGALESE_START_MARKERS):
            ignore_section = True
            continue
        elif any(line.startswith(token) for token in LEGALESE_END_MARKERS):
            ignore_section = False
            continue

        if not ignore_section:
            out.append(line.rstrip(sep))
            i += 1

    return sep.join(out)

def clean_text(text):
    return " ".join(text.split())


if __name__ == "__main__":
    print(clean_read("D:\\Research_Projects\\ArsenyProjects\\books\\3200.txt"))

