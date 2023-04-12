#import entity_replacement
from utils.BookProcessing import chunk_book, rechunk_book
from gpt_api_processing import SummarizeChunk, SummarizeChunkRetry, CreateFalseSummary
import json

from settings import column_separator, fake_summary_separator, line_separator

class BookProcessor():

    def __init__(self, original_book_text, scene_recognition_questions_per_chunk=4, chunk_length=3000, overlap_symbols=300, live_mode=False):
        '''This class takes a raw book data, processes it and creates questions. It is used to add new books to the dataset. Use ProcessedBookLoader to load data and associated questions for a book that was already processed.'''

        self.questions_per_chunk = 8
        self.original_book_text = 8

        #self.NE_sub_dict = entity_replacement.create_ne_sub_dict(original_book_text)
        self.NE_sub_dict = None

        self.max_chunk_length = chunk_length
        self.book_chunks = rechunk_book(chunk_book(original_book_text, self.max_chunk_length), self.max_chunk_length)

        self.overlapped_book_chunks = []  # same as book chunks, but with overlap. Will be filled together with data (summary) creation

        self.book_chunk_summaries = []
        self.false_book_chunk_summaries = []

        self.book_summary_so_far = None

        self.failed_summaries = {} # Dict index: comment for failed summaries

        # The chunks are slightly overlapped when summaries are created since we don't know exactly where different scenes end and other scenes begin.
        self.overlap_symbols = overlap_symbols

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
                current_chunk = self.book_chunks[current_chunk_index - 1][-self.overlap_symbols:] + current_chunk

            if current_chunk_index < len(self.book_chunks) - 1:
                current_chunk = current_chunk + self.book_chunks[current_chunk_index + 1][:self.overlap_symbols]

            try:
                self.book_chunk_summaries.append(SummarizeChunk(current_chunk))
                self.overlapped_book_chunks.append(current_chunk)

            except ValueError as first_error:

                print("Retrying to force re-summarize chunk")

                failures = 0
                while failures < 3:

                    try:
                        summary, warning = SummarizeChunkRetry(current_chunk)

                        self.book_chunk_summaries.append(summary)
                        self.overlapped_book_chunks.append(current_chunk)

                        if warning is not None:
                            self.failed_summaries[len(self.book_chunk_summaries)-1] = warning
                        else:
                            print("Successfully re-summarized the chunk using a more forceful request.")
                        break

                    except ValueError as e:
                        print(e)
                        print("Retrying to summarize chunk")
                        failures += 1

                if failures == 3:
                    self.book_chunk_summaries.append(None)
                    self.overlapped_book_chunks.append(current_chunk)
                    self.failed_summaries[(len(self.book_chunk_summaries) - 1)] = "Complete failure."
                    print("Failed to summarize chunk")

    def create_false_book_chunk_summaries(self):
        if not self.book_chunk_summaries:
            raise ValueError("Book chunk summaries must be created before generating questions.")

        for i, summary in enumerate(self.book_chunk_summaries):
            if summary is None:
                self.false_book_chunk_summaries.append(None)
            else:
                self.false_book_chunk_summaries.append(list())

                num_false_summaries = max(1, 9 - i) # The first ones need more false summaries as they will be used more often.

                for _ in range(num_false_summaries):
                    try:
                        self.false_book_chunk_summaries[-1].append(CreateFalseSummary(summary))
                    except ValueError as e:
                        print("Failed to create a false summary {}".format(e))

                if not self.false_book_chunk_summaries[-1]:
                    self.false_book_chunk_summaries[-1] = None
                    self.failed_summaries[i] = "Failed to create any fake summaries."
    def save_summary_data(self, file_path):

        columns = ["ChunkInd", "BookChunks", "OverlappedBookChunks", "Summaries", "FakeSummaries", "Failure", "Comment"]

        if not self.overlapped_book_chunks or not self.book_chunk_summaries or not self.false_book_chunk_summaries:
            raise ValueError("Data must be filled first!")

        book_chunks_tmp = self.book_chunks[:len(self.overlapped_book_chunks)]

        with open(file_path, "w") as f:
            f.write(column_separator.join(columns))
            f.write(line_separator)

            for i, (chunk, ochunk, sum, fakesums) in enumerate(zip(book_chunks_tmp, self.overlapped_book_chunks, self.book_chunk_summaries, self.false_book_chunk_summaries)):

                chunk, ochunk, sum = [el.strip() if el else el for el in (chunk, ochunk, sum)]
                fakesums = [el.strip() for el in fakesums] if fakesums else fakesums

                if i in self.failed_summaries:
                    if self.failed_summaries[i] == "Complete failure.":
                        f.write(column_separator.join([str(i), chunk, ochunk, "", "", "Fail", self.failed_summaries[i]]))
                    else:
                        f.write(column_separator.join([str(i), chunk, ochunk, sum, fake_summary_separator.join([str(fs) for fs in fakesums if fs]), "Warning", self.failed_summaries[i]]))
                else:
                    f.write(column_separator.join([str(i), chunk, ochunk, sum, fake_summary_separator.join([str(fs) for fs in fakesums if fs]), "OK", ""]))

                f.write(line_separator)

    def create_recognition_questions(self):
        ''' Creates recognition questions:
         One from immediate past
         One from the same book segment (quarter)
         Two from previous segments
         Each question has the associated memory length variable, indicating how many chunks ago
         the event that is being tested was introduced in the book.'''

        if not self.book_chunk_summaries:
            raise ValueError("Book chunk summaries and false book chunk summaries must be created before generating questions.")

        num_chunks_to_process = len(self.book_chunks) if self.live_mode else 10
        raise NotImplementedError() # Finish

def LoadSummaries(filepath):

    with open(filepath, "r") as f:
        raw = f.read()

        lines = raw.split(line_separator)

        rowids, chunks, ochunks, sums, fakesums, status, comment = zip(*[l.split(column_separator) for l in lines if l])



    fakesums_unrolled = [fk.split(fake_summary_separator) for fk in fakesums]

    return rowids, chunks, ochunks, sums, fakesums_unrolled, status, comment





if __name__ == "__main__":
    with open("Data/RawBooks/ScifiExampleRaw.txt", "r") as f:
        b = f.read()


    book_processor = BookProcessor(b, live_mode=False)
    book_processor.create_chunk_summaries()
    book_processor.create_false_book_chunk_summaries()

    book_processor.save_summary_data("./Data/TrueAndFalseSummaryData/ScifiExampleProcessed.tagseparated")

    rowids, chunks, ochunks, sums, fakesums_unrolled, status, comment = LoadSummaries("./Data/TrueAndFalseSummaryData/ScifiExampleProcessed.tagseparated")
    res = LoadSummaries("./Data/TrueAndFalseSummaryData/ScifiExampleProcessed.tagseparated")



    #
    # with open("Data/AnalysisExamples/DeadStarRover10sums.txt", "w") as f:
    #     true_summary_lines = (["Chunk {}, True Summary: {}\n".format(num, summary.strip()) for num, summary in enumerate(book_processor.book_chunk_summaries)])
    #     f.writelines(true_summary_lines)
    #
    # with open("Data/AnalysisExamples/DeadStarRoverFalseSums.txt", "w") as f:
    #
    #     lines = ["\n".join(["Chunk {}, False Summary {}: {}".format(chunkn, sumn, summary) for sumn, summary in enumerate(false_sums)]) for chunkn, false_sums in enumerate(book_processor.false_book_chunk_summaries)]
    #     f.writelines(lines)
    #
    # with open("Data/AnalysisExamples/DeadStarRover10_true_and_false_sums.txt", "w") as f:
    #     true_and_false = [t + f for t, f in zip(true_summary_lines, lines)]
    #     f.writelines(true_and_false)

   # Also can recursively summarize summaries with
   #SummarizeSummaries(book_chunk_summaries or meta_summaries, max_length=10000 or 20000)


