from Dataloaders import *

#import Dataloaders as dl

import os
import time

from gpt_api_processing import SimplifySummary

### !!! IMPORTANT !!! ###
# Change this to the appropriate folder. Make sure not to double-process the same books #



fancy_summaries_folder_to_process = "SummariesToSimplify"
simplified_summaries_folder_to_save = "SimplifiedSummaries"

# Change this to the appropriate folder. Make sure not to double-process the same books #

if __name__ == "__main__":

    fancy_summaries_path = os.path.join("Data", fancy_summaries_folder_to_process)
    fancy_summaries_to_process = [f for f in os.listdir(fancy_summaries_path) if os.path.isfile(os.path.join(fancy_summaries_path, f))]


    sumpath = os.path.join("Data", simplified_summaries_folder_to_save)
    simplified_books = [f for f in os.listdir(sumpath) if os.path.isfile(os.path.join(sumpath, f))]
    simplified_books = set([n.split(".tagseparated_simplified")[0] for n in simplified_books])

    books_to_process = [b for b in fancy_summaries_to_process if b.split(".tagseparated")[0] not in simplified_books]

    #bookpaths_to_process = [os.path.join(bookpath, b) for b in books_to_process]

    for k, bname in enumerate(books_to_process):

        print("Preparing to process book {} ({} out of {}).".format(bname, k, len(books_to_process)))

        try:

            bpath = os.path.join(fancy_summaries_path, bname)
            b = BookProcessor.init_from_summaries(bpath)

            t0 = time.time()

            for i in range(len(b.book_chunk_summaries)):

                fancy_summary = b.book_chunk_summaries[i]
                simplified_summary = SimplifySummary(fancy_summary)

                b.book_chunk_summaries[i] = simplified_summary

            t1 = time.time()
            print("Simplified summaries in {} minutes.".format((t1 - t0) / 60))

            bname_simpl = bname + "_simplified"
            sumpath_tmp = os.path.join(sumpath, bname_simpl)

            b.save_summary_data(sumpath_tmp)

        except Exception as e:
            print("Failed to process book {}".format(bname))

            print("Exception of type: {}, {}".format(type(e).__name__, e))

    #b2 = BookProcessor.init_from_summaries("./Data/TrueAndFalseSummaryData/297_v2.tagseparated")