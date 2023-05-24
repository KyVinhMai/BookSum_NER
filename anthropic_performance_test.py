import anthropic
from settings import OCHUNK_OVERLAP_SYMBOLS
import os
from utils.helper_functions import PreppedQuestions, read_shortform_questions

import csv


import numpy as np


# Do ~ 1000 questions with ~10k context

def ask_question(client, context, questions, model="claude-instant-v1.1-100k"):

    questions_str = "".join(["\nQuestion {}: {}\n".format(i + 1, q) for i, q in enumerate(questions)])

    prompt = "{} You will read a large part of a book, after which I will ask you questions about what you've read. Book part:\n{} \nQuestions:{}\nWrite only the numerical answers to the corresponding questions, separating them by commas. For example, '1,3,4'. Begin your answers with a {} tag. {}".format(
            anthropic.HUMAN_PROMPT, context, questions_str, "###BEGIN_ANSWER###", anthropic.AI_PROMPT)

    return "1,2,3" # TODO - change to production later
    #print(prompt)
    #return
    resp = client.completion(
        prompt=prompt,
        stop_sequences=[anthropic.HUMAN_PROMPT],
        model=model,
        max_tokens_to_sample=150,
    )


    answer_text = resp["completion"]
    #print(answer_text)
    if "###BEGIN_ANSWER###" not in answer_text:
        print("Wrong answer format")
        return None
    answer_text = answer_text.split("###BEGIN_ANSWER###")[1]
    answer_text = answer_text.split("###END_ANSWER###")[0]
    return answer_text.strip()


def get_random_questions(question_folder, whentoask=10):

    assert whentoask >= 2
    '''Gets a few random questions (usually 3), associated with a specific reading time in a random book'''
    path = os.path.join(question_folder)

    root, dirs, files = next(os.walk(path))

    chosen_book = np.random.choice(files)
    questions = read_shortform_questions(os.path.join(root, chosen_book))


    if (questions.raw_chunk[whentoask-1][-OCHUNK_OVERLAP_SYMBOLS:] != questions.overlapped_chunk[whentoask][:OCHUNK_OVERLAP_SYMBOLS]):

        context = " ".join(questions.raw_chunk[0:whentoask - 1])
        last_chunk = questions.overlapped_chunk[whentoask]
        last_chunk_prefix = last_chunk[:50]
        context = context[:context.find(last_chunk_prefix)] + last_chunk
    else:
        context = " ".join(questions.raw_chunk[0:whentoask - 1] + (questions.overlapped_chunk[whentoask][:OCHUNK_OVERLAP_SYMBOLS],))

    questions_strings = questions.questions[whentoask]
    answers = questions.answers[whentoask]
    memloads = questions.memory_loads[whentoask]
    question_types = questions.question_types[whentoask]

    return chosen_book, context, questions_strings, answers, memloads, question_types




if __name__ == "__main__":
    with open("./anthropicKEY") as f:
        client = anthropic.Client(api_key=f.read().strip())

    if False:
        resp = ask_question(client, "Mary and Jane went to the store. They wanted to buy food, but it turned out that they did not have any money.", ["Who went to the store?\n1) Peter and Caren\n2) Chloe and Charles\n3) Mary and Jane", "What did the characters want?\n1) Booze\n2)Food"])
        print(resp)

    c_whenaskeds = ["WhenAsked"]
    c_qbookfile = ["BookQuestionsFile"]
    c_contextlengths = ["ContextLength"]
    c_memloads = ["RetentionDelay"]
    c_trueanswers = ["CorrectAnswer"]
    c_modelanswers = ["ModelAnswer"]
    c_questiontypes = ["QuestionType"]
    c_contexts = ["Contexts"]


    for whentoask in [2, 10]:
        for i in range(10):
            chosen_book, context, questions_strings, answers, memloads, question_types = get_random_questions("./Data/TmpQuestions/raw/shortform", whentoask=whentoask)
            model_ans = ask_question(client, context, questions_strings, model="claude-v1.3-100k")

            #print("True answers: {}, model answers: {}".format(answers, model_ans))

            if len(model_ans.split(",")) != len(answers):
                model_ans = ["NA" for _ in answers]
            else:
                model_ans = [str(el).strip() for el in model_ans.split(",")]

            contlen = len(context.split())
            for mans, ans, mem, qtype in zip(model_ans, answers, memloads, question_types):

                ## Same for each query
                c_whenaskeds.append(whentoask)
                c_qbookfile.append(chosen_book)
                c_contextlengths.append(contlen)
                c_contexts.append("{}".format(context))

                ## Vary per question within one query
                c_memloads.append(mem)
                c_questiontypes.append(qtype)
                c_trueanswers.append(ans)
                c_modelanswers.append(mans)


    with open("Results/anthropic_tests_unsubstituted.csv", "w", newline='') as csvfile:

        writer = csv.writer(csvfile, delimiter=",")
        for elts in zip(c_whenaskeds, c_qbookfile, c_contextlengths, c_memloads, c_trueanswers, c_modelanswers, c_questiontypes):

            writer.writerow(list(elts))

    with open("Results/anthropic_tests_unsubstituted_withcontext.csv", "w", newline='') as csvfile:

        writer = csv.writer(csvfile, delimiter=chr(255))
        for elts in zip(c_whenaskeds, c_qbookfile, c_contextlengths, c_memloads, c_trueanswers, c_modelanswers, c_questiontypes, c_contexts):
            writer.writerow(list(elts))

    reconstructed_contexts = []
    reconstucted_mans = []
    with open("Results/anthropic_tests_unsubstituted_withcontext.csv", newline='') as csvfile:

        reader = csv.reader(csvfile, delimiter=chr(255))
        for row in reader:

            reconstucted_mans.append(row[-3])
            reconstructed_contexts.append(row[-1])

    ## TODO - save one with questions as well? (For fine-tuning?)


    print(reconstructed_contexts == c_contexts, c_modelanswers == reconstucted_mans)
    # reconstructed_contexts = []
    # with open("Results/anthropic_tests_unsubstituted.csv", newline='') as csvfile:
    #
    #     reader = csv.reader(csvfile, delimiter=",")
    #     for row in reader:
    #         reconstructed_contexts.append(row[-1])





