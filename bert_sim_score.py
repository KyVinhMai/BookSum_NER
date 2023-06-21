from evaluate import load
bertscore = load("bertscore")

import os
import settings

import openai
import pickle as pkl

from collections import namedtuple

HierarchicalSummaries = namedtuple("HierarchicalSummaries", ["summaries", "false_summaries", "summary_levels"])

with open("../GPTkeys/mm_key.txt", "r") as f:
    openai.api_key = f.read().strip()


def reconstruct_summary_gpt(false_summary):

    prompt = "You will read a summary that covers a part of a book, but misrepresents events in it. Correct it so that it accurately represents the book events:\nIncorrect summary: '{}'\n\nYou will not have access to the original book, but try to do your best.\n\nWrite only the corrected summary, do not explain your solution.\nBegin your corrected summary answer with a {} tag.".format(false_summary, "###BEGIN_ANSWER###")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        temperature=0.0,
        messages=[
          {"role": "system", "content": "You are a helpful assistant that corrects innaccurate book part summaries. Begin your answer with a {} tag.".format("###BEGIN_ANSWER###")},
          {"role": "user", "content": prompt} # Add "in under 500 words?
        ]
    )

    response_content = response["choices"][0]["message"]["content"]

    answer_text = response_content.split("###BEGIN_ANSWER###")[1]
    answer_text = answer_text.split("###END_ANSWER###")[0]

    return answer_text

def reconstruct_summary_gpt_withcontext(false_summary, lastrawchunk):

    prompt = "You will read a summary that covers a part of a book, but misrepresents events in it. Correct it so that it accurately represents the book events:\n\nIncorrect summary: '{}'\n\nOriginal book snippet:\n'{}'\n\nWrite only the corrected summary, do not explain your solution.\nBegin your corrected summary answer with a {} tag.".format(false_summary, lastrawchunk, "###BEGIN_ANSWER###")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        temperature=0.0,
        messages=[
          {"role": "system", "content": "You are a helpful assistant that corrects innaccurate book part summaries. Begin your answer with a {} tag.".format("###BEGIN_ANSWER###")},
          {"role": "user", "content": prompt} # Add "in under 500 words?
        ]
    )

    response_content = response["choices"][0]["message"]["content"]

    answer_text = response_content.split("###BEGIN_ANSWER###")[1]
    answer_text = answer_text.split("###END_ANSWER###")[0]

    return answer_text


def load_hierarch_summaries(hierarch_sum_folder, ent_dict_folder, num_to_process=15, start_at=0):

    entpath = os.path.join("Data", ent_dict_folder)
    hsumpath = os.path.join("Data", hierarch_sum_folder)

    sumf_to_process = [f for f in os.listdir(hsumpath) if os.path.isfile(os.path.join(hsumpath, f))]
    sumf_to_process = sumf_to_process[start_at:num_to_process]

    summaries_to_process = [os.path.join(hsumpath, f) for f in sumf_to_process]
    ent_dicts_to_process = [os.path.join(entpath, f.split(".")[0] + ".repl") for f in sumf_to_process]

    assert all([os.path.isfile(f) for f in ent_dicts_to_process]), 'Missing a preprocessed replacement dictionary {}'.format(ent_dicts_to_process)

    ent_rep_dicts = []

    for p in ent_dicts_to_process:
        with open(p, "rb") as f:
            ent_rep_dicts.append(pkl.load(f))

    hsums = []

    for f in summaries_to_process:
        with open(f, "r") as sumfile:
            lines = sumfile.read().split(settings.line_separator)[1:] # Ignore the header column

            true_sums, false_sums, levels = list(zip(*[el.split(settings.column_separator) for el in lines if el]))

            hsums.append(HierarchicalSummaries(true_sums, false_sums, levels))

    return hsums, ent_rep_dicts, sumf_to_process



if __name__ == "__main__":

    with open("./lastchunk_tmp_.txt", "r") as f:
        lastchunk = f.read()

    true_sum = "The excerpt speaks of the magical and persuasive lies told by the arrival of Spring, which promises renewal and perfection. The narrator is drawn by the lure of finding his 'Perfect Woman.' He reminisces about his first love but decides to not speak of it at the moment. Instead, he lays down to eat, drink, and dream in a dingle, wondering about what kind of girl the Golden Girl would be."
    false_sum = "The excerpt describes a dreary, cold winter day, with no sign of warmth or life. The narrator longs to escape to a place of perpetual summer, where the sun shines and endless opportunities abound. He thinks of his desire to travel and explore the world, but ultimately decides to stay put and focus on his work at hand. He spends his day dreaming of exotic lands and the adventures that await him there."

    reconstructed = reconstruct_summary_gpt(false_sum)
    reconstructed_with_c = reconstruct_summary_gpt_withcontext(false_sum, lastchunk)

    predictions = [false_sum, reconstructed, reconstructed_with_c]
    references = [true_sum, true_sum, true_sum]

    #
    #
    # predictions = ["hello there, you!", "general kenobi"]
    # references = ["hello there", "general kenobi"]
    results = bertscore.compute(predictions=predictions, references=references, lang="en")
    print(results)

    # Use improvement relatively to the false to true similarity.
    # Look at hierarchical sums separately. Hopefully their stuff does not change.