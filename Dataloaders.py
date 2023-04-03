#import entity_replacement
from utils.BookProcessing import chunk_book, rechunk_book
from gpt_api_processing import SummarizeChunk
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

            current_chunk = self.book_chunks[current_chunk_index]

            if current_chunk_index > 0:
                current_chunk = self.book_chunks[current_chunk_index - 1][-300:] + current_chunk

            if current_chunk_index < len(self.book_chunks) - 1:
                current_chunk = current_chunk + self.book_chunks[current_chunk_index + 1][:300]

            self.book_chunk_summaries.append(SummarizeChunk(current_chunk))
            self.current_chunk_index += 1

    def create_recognition_questions(self):
        ''' Creates recognition questions:
         One from immediate past
         One from the same book segment (quarter)
         Two from previous segments
         Each question has the associated memory length variable, indicating how many chunks ago
         the event that is being tested was introduced in the book.'''

        num_chunks_to_process = len(self.book_chunks) if self.live_mode else 10


if __name__ == "__main__":
    with open("Data/RawBooks/Example.txt", "r") as f:
        b = f.read()

    book_processor = BookProcessor(b, live_mode=False)
    book_processor.create_chunk_summaries()




