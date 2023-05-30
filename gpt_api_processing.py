import os
import openai

from utils.BookProcessing import rechunk_book

BEGIN_ANSWER_TAG = "### BEGIN ANSWER ###"

openai.api_key = os.getenv("OPENAI_API_KEY")

# openai.api_key_path = "../gptapikey"

with open("../GPTkeys/ar_key.txt", "r") as f:
  openai.api_key = f.read().strip()

with open("test.txt", "r") as f:
  text = f.read()

def ParaphraseChunk(chunk):
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system",
       "content": "You are a helpful assistant that paraphrases book snippets. Begin your answer with a {} tag.".format(BEGIN_ANSWER_TAG)},
      {"role": "user", "content": 'Paraphrase the following book excerpt: "{}"'.format(chunk)}
    ]
  )

  response_content = response["choices"][0]["message"]["content"]

  if BEGIN_ANSWER_TAG not in response_content:
    raise ValueError("GPT response does not have a {} tag".format(BEGIN_ANSWER_TAG))

  resp_parts = response_content.split(BEGIN_ANSWER_TAG)

  if len(resp_parts) != 2:
    raise ValueError("GPT gave multiple {} tags".format(BEGIN_ANSWER_TAG))

  answer = resp_parts[-1]

  if not answer.strip():
    raise ValueError("GPT gave an empty response")

  return answer


def SummarizeChunk(chunk):
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": "You are a helpful assistant that summarizes book snippets. Begin your answer with a {} tag.".format(BEGIN_ANSWER_TAG)},
      {"role": "user", "content": 'Summarize the following book excerpt: "{}". Start your answer with a "{}" tag.'.format(chunk, BEGIN_ANSWER_TAG)} # Add "in under 500 words?
    ]
  )

  response_content = response["choices"][0]["message"]["content"]

  if BEGIN_ANSWER_TAG not in response_content:

    raise ValueError("GPT response does not have a {} tag. Response: {}".format(BEGIN_ANSWER_TAG, response_content))

  resp_parts = response_content.split(BEGIN_ANSWER_TAG)

  if len(resp_parts) != 2:
    raise ValueError("GPT gave multiple {} tags".format(BEGIN_ANSWER_TAG))

  answer = resp_parts[-1]

  if not answer.strip():
    raise ValueError("GPT gave an empty response")

  return answer

def SummarizeChunkRetry(chunk):
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": "You are a helpful assistant that summarizes book snippets. Begin your answer with a {} tag.".format(BEGIN_ANSWER_TAG)},
      {"role": "user", "content": 'Summarize the following book excerpt: "{}". Make sure to begin your answer with a {} tag!'.format(chunk, BEGIN_ANSWER_TAG)} # Add "in under 500 words?
    ]
  )

  response_content = response["choices"][0]["message"]["content"]

  if BEGIN_ANSWER_TAG not in response_content:

    return response_content, "GPT response does not have a {} tag. Response: {}".format(BEGIN_ANSWER_TAG, response_content)

  resp_parts = response_content.split(BEGIN_ANSWER_TAG)

  if len(resp_parts) != 2:
    raise ValueError("GPT gave multiple {} tags".format(BEGIN_ANSWER_TAG))

  answer = resp_parts[-1]

  if not answer.strip():
    raise ValueError("GPT gave an empty response")

  return answer, None

def SummarizeSummaries(chunk_summaries, max_length=10000):

  meta_chunks = rechunk_book(["Summary {}: {}\n".format(ind, summary) for ind, summary in enumerate(chunk_summaries)], max_length)
  result = []

  for ind, m in enumerate(meta_chunks):
    if ind % 10 == 0:
      print("Processed {} meta chunks".format(ind + 1))

    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system",
         "content": "You are a helpful assistant that summarizes book scene summaries. Begin your answer with a {} tag.".format(
           BEGIN_ANSWER_TAG)},
        {"role": "user",
         "content": 'Summarize the following book excerpt summaries into one summary: "{}". Make sure to begin your answer with a {} tag!'.format(m, BEGIN_ANSWER_TAG)}  # Add "in under 500 words?
      ]
    )
    result.append(response["choices"][0]["message"]["content"])

  return result

def CreateFalseSummary(chunk):
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": "You are a helpful assistant that changes book snippet summaries. Begin your answer with a {} tag.".format(BEGIN_ANSWER_TAG)},
      {"role": "user", "content": 'Take the summary below and rephrase it in such a way that the described events are no longer the same, even though the setting remains the same. Keep your summary to the same length. Start your answer with a "{}" tag. \nInital summary: \n"{}"'.format(BEGIN_ANSWER_TAG, chunk)} # Add "in under 500 words?
    ]
  )

  response_content = response["choices"][0]["message"]["content"]

  if BEGIN_ANSWER_TAG not in response_content:
    raise ValueError("GPT response does not have a {} tag".format(BEGIN_ANSWER_TAG))

  resp_parts = response_content.split(BEGIN_ANSWER_TAG)

  if len(resp_parts) != 2:
    raise ValueError("GPT gave multiple {} tags".format(BEGIN_ANSWER_TAG))

  answer = resp_parts[-1]

  answer = answer.split("### END ANSWER ###")[0] ### GPT 3 sometimes randomly appends this, for whatever reason.

  if not answer.strip():
    raise ValueError("GPT gave an empty response")
  
  return answer.strip()



def DescribeChunkRoleFreeform(book_summary, scene_summary):
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system",
       "content": "You are a helpful assistant that analyses how book snippets relate to the general book plot. Begin your answer with a {} tag.".format(BEGIN_ANSWER_TAG)},
      {"role": "user", "content": 'Book summary: {}\nScene summary: {}\nIs this scene crucial to the plot? How does it advance the plot?'.format(book_summary, scene_summary)}
    ]
  )

  response_content = response["choices"][0]["message"]["content"]

  if BEGIN_ANSWER_TAG not in response_content:
    raise ValueError("GPT response does not have a {} tag".format(BEGIN_ANSWER_TAG))

  resp_parts = response_content.split(BEGIN_ANSWER_TAG)

  if len(resp_parts) != 2:
    raise ValueError("GPT gave multiple {} tags".format(BEGIN_ANSWER_TAG))

  answer = resp_parts[-1]

  if not answer.strip():
    raise ValueError("GPT gave an empty response")

  return answer


def SimplifySummary(initial_summary):
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system",
       "content": "You are a helpful assistant that changes book snippet summaries. Begin your answer with a {} tag.".format(
         BEGIN_ANSWER_TAG)},
      {"role": "user",
       "content": 'Paraphrase the summary below to have the same meaning but avoid rare words and fancy language. Begin your answer with a "{}" tag. \nInital summary: \n"{}"'.format(
         BEGIN_ANSWER_TAG, initial_summary)}
    ]
  )

  response_content = response["choices"][0]["message"]["content"]

  if BEGIN_ANSWER_TAG not in response_content:
    raise ValueError("GPT response does not have a {} tag".format(BEGIN_ANSWER_TAG))

  resp_parts = response_content.split(BEGIN_ANSWER_TAG)

  if len(resp_parts) != 2:
    raise ValueError("GPT gave multiple {} tags".format(BEGIN_ANSWER_TAG))

  answer = resp_parts[-1]

  answer = answer.split("### END ANSWER ###")[0]  ### GPT 3 sometimes randomly appends this, for whatever reason.

  if not answer.strip():
    raise ValueError("GPT gave an empty response")

  return answer.strip()

