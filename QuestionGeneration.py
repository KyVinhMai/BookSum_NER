import random

import Dataloaders as dl
import settings

import numpy as np
random.seed(42)
np.random.seed(42)

class RecognitionQuestion:

    def __init__(self, correct_answer, decoys, decoy_types, when_asked, retention_delay):

        self.correct_answer = correct_answer
        self.decoys = decoys
        self.decoy_types = decoy_types
        self.when_asked = when_asked
        self.retention_delay = when_asked

        self.is_mixed = True if len(set(decoy_types)) == 1 else False

        self.n_options = len(self.decoys) + 1
        self.true_ans_position = np.random.randint(self.n_options)

        self.all_options = decoys.copy()
        self.all_options.insert(self.true_ans_position, correct_answer)


    def question_string(self):
        return "".join(["Which of the following scenes were in the book?\n"] + [str(i + 1) + ") " + self.all_options[i] + "\n" for i in range(self.n_options)])

    def __str__(self):

        answer = "Answer:" + str(self.true_ans_position + 1)

        return self.question_string() + answer



class RecognitionQuestionGenerator:

    def __init__(self, book_processors):
        '''Takes a list of book processors (already with true and fake summaries generated. Generates questions based on that.'''
        self.book_processors

