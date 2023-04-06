#import entity_replacement
from utils.BookProcessing import chunk_book, rechunk_book
from gpt_api_processing import SummarizeChunk, SummarizeChunkRetry
import json


class BookProcessor():

    def __init__(self, original_book_text, scene_recognition_questions_per_chunk=4, chunk_length=3000, overlap_symbols=300, live_mode=False):
        '''This class takes a raw book data, processes it and creates questions. It is used to add new books to the dataset. Use ProcessedBookLoader to load data and associated questions for a book that was already processed.'''

        self.questions_per_chunk = 8
        self.original_book_text = 8

        #self.NE_sub_dict = entity_replacement.create_ne_sub_dict(original_book_text)
        self.NE_sub_dict = None

        self.max_chunk_length = chunk_length
        self.book_chunks = rechunk_book(chunk_book(original_book_text, self.max_chunk_length), self.max_chunk_length)

        self.book_chunk_summaries = []

        self.book_summary_so_far = None

        self.failed_summary_inds = list()
        self.failed_summary_comments = list()


        self.data_list = []

        self.live_mode = live_mode
    def ne_sub(self, chunk):
        ### Substitute NE using this book entity sub map
        ### Can be used to substitute NE's from this book into another.
        ### In this case, if a (non-exception) NE in the chunk is identified,
        ### it is substituted with a random NE from the book
        raise NotImplementedError

        return entity_replacement.replace_ne(self.NE_sub_dict, chunk)

    def create_chunk_summaries(self):

        num_chunks_to_process = len(self.book_chunks) if self.live_mode else 10

        for current_chunk_index in range(num_chunks_to_process):

            if current_chunk_index % 10 == 0:
                print("Current index: {} out of {}".format(current_chunk_index + 1, num_chunks_to_process))

            current_chunk = self.book_chunks[current_chunk_index]

            if current_chunk_index > 0:
                current_chunk = self.book_chunks[current_chunk_index - 1][-300:] + current_chunk

            if current_chunk_index < len(self.book_chunks) - 1:
                current_chunk = current_chunk + self.book_chunks[current_chunk_index + 1][:300]

            try:
                self.book_chunk_summaries.append(SummarizeChunk(current_chunk))

            except ValueError as first_error:

                print("Retrying to force re-summarize chunk")

                failures = 0
                while failures < 3:

                    try:
                        summary, warning = SummarizeChunkRetry(current_chunk)

                        self.book_chunk_summaries.append(summary)

                        if warning is not None:
                            self.failed_summary_inds.append(len(self.book_chunk_summaries) -1)
                            self.failed_summary_comments.append(warning)
                        else:
                            print("Successfully re-summarized the chunk using a more forceful request.")
                        break

                    except ValueError as e:
                        print(e)
                        print("Retrying to summarize chunk")
                        failures += 1

                if failures == 3:
                    self.book_chunk_summaries.append("This book chunk can not be summarized.")
                    self.failed_summary_inds.append(len(self.book_chunk_summaries) - 1)
                    self.failed_summary_comments.append("Complete failure.")
                    print("Failed to summarize chunk")

    def create_recognition_questions(self):
        ''' Creates recognition questions:
         One from immediate past
         One from the same book segment (quarter)
         Two from previous segments
         Each question has the associated memory length variable, indicating how many chunks ago
         the event that is being tested was introduced in the book.'''

        num_chunks_to_process = len(self.book_chunks) if self.live_mode else 10
        raise NotImplementedError() # Finish

if __name__ == "__main__":
    with open("Data/RawBooks/Example.txt", "r") as f:
        b = f.read()


    if False:
        book_processor = BookProcessor(b, live_mode=True)
        book_processor.create_chunk_summaries()

       # with open("Data/AnalysisExamples/PrideAndPrejudiceSummaries.txt", "w") as f:
       #     f.writelines(book_processor.book_chunk_summaries)




