from Dataloaders import *

import os
import time

### !!! IMPORTANT !!! ###
# Change this to the appropriate folder. Make sure not to double-process the same books #

book_folder_to_process = "DoubleChecked2"

# Change this to the appropriate folder. Make sure not to double-process the same books #

if __name__ == "__main__":

    bookpath = os.path.join("Data", book_folder_to_process)
    books_to_process = [f for f in os.listdir(bookpath) if os.path.isfile(os.path.join(bookpath, f))]

    sumpath = os.path.join("Data", "TrueAndFalseSummaryData")
    processed_books = [f for f in os.listdir(sumpath) if os.path.isfile(os.path.join(sumpath, f))]
    processed_books = set([n.strip(".tagseparated") for n in processed_books])

    books_to_process = [b for b in books_to_process if b.strip(".txt") not in processed_books]

    #bookpaths_to_process = [os.path.join(bookpath, b) for b in books_to_process]

    for k, bname in enumerate(books_to_process):

        print("Preparing to process book {} ({} out of {}).".format(bname, k, len(books_to_process)))

        try:

            bpath = os.path.join(bookpath, bname)

            with open(bpath, "r") as f:
                b = f.read()

            t0 = time.time()

            book_processor = BookProcessor(b, live_mode=True)
            book_processor.create_chunk_summaries()

            t1 = time.time()
            print("Created chunk summaries in {} minutes".format((t1-t0)/60))
            book_processor.create_false_book_chunk_summaries()

            t2 = time.time()
            print("Created false chunk summaries in {} minutes".format((t2 - t1) / 60))

            bname_tag = bname.strip("txt") + "tagseparated"
            sumpath_tmp = os.path.join(sumpath, bname_tag)

            book_processor.save_summary_data(sumpath_tmp)

        except Exception as e:
            print("Failed to process book {}".format(bname))

            print("Exception of type: {}, {}".format(type(e).__name__, e))

    #b2 = BookProcessor.init_from_summaries("./Data/TrueAndFalseSummaryData/297_v2.tagseparated")