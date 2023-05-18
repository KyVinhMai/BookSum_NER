import anthropic
import settings

# Do ~ 1000 questions with ~10k context

with open("./antrokey") as f:
    client = anthropic.Client(api_key=f.read().strip())

    resp = client.completion(
        prompt="{} You will read a large part of a book, after which I will ask you questions about what you've read. Book part:\nMary and Jane went to the store. They wanted to buy food, but it turned out that they did not have any money. \nQuestions:\n\nQuestion 1: Who went to the store?\n1) Peter and Caren\n2) Chloe and Charles\n3) Mary and Jane\n\nQuestion 2: What did the characters want?\n1) Booze\n2)Food\n\nWrite only the numerical answers to the corresponding questions, separating them by commas. For example, '1,3,4'. Begin your answers with a {} tag. {}".format(anthropic.HUMAN_PROMPT, "###BEGIN_ANSWER###", anthropic.AI_PROMPT),
        stop_sequences=[anthropic.HUMAN_PROMPT],
        model="claude-instant-v1.1-100k",
        max_tokens_to_sample=150,
    )

print(resp)