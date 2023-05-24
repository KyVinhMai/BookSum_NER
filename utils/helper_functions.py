from settings import line_separator, column_separator, fake_summary_separator

from collections import namedtuple

PreppedQuestions = namedtuple("PreppedQuestions", ["whenasked", "raw_chunk", "overlapped_chunk", "questions", "answers", "question_types", "memory_loads"])

def read_shortform_questions(path):

    with open(path, "r") as f:

        raw = f.read()

        lines = raw.split(line_separator)
        #rowids, chunks, ochunks, sums, fakesums, status, comment = LoadSummaries(filepath)
        whenasked, chunks, ochunks, questions, answers, qtypes, memoloads = zip(*[l.split(column_separator) for l in lines if l])

        # Dropping the first line since it's the column name
        whenasked, chunks, ochunks, questions, answers, qtypes, memoloads = [el[1:] for el in (whenasked, chunks, ochunks, questions, answers, qtypes, memoloads)]

        questions, answers, qtypes, memoloads =  [[el.split(fake_summary_separator) for el in col] for col in (questions, answers, qtypes, memoloads)]
        #"WHEN_ASKED", "RAW_CHUNK", "OVERLAPPED_CHUNK", "QUESTIONS", "QUESTION_ANSWERS", "QUESTION_TYPES", "MEMLOADS"

        return PreppedQuestions(whenasked, chunks, ochunks, questions, answers, qtypes, memoloads)

if __name__ == "__main__":
    # Usage
    res = read_shortform_questions("../Data/TmpQuestions/substituted/shortform/2960.questions_shortform")
    #res.questions - list of lists of questions. Outer list - steps in reading the book, inner - up to 3 questions associated with each step.