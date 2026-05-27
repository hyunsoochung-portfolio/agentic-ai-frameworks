"""A minimal multi-turn chat loop built directly on the OpenAI SDK.

This is the second step from the blog series (after the first single-call
example): it keeps a running `messages` list so the model retains the
conversation context across turns. Type "q" to quit.

Note: as the conversation grows, the `messages` list grows cumulatively,
which eventually leads to a large/expensive context. Managing that is one
of the things a framework later abstracts away.
"""

import openai

client = openai.OpenAI()

messages = []


def call_ai():
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    message = response.choices[0].message.content
    messages.append({"role": "assistant", "content": message})
    print(f"ai: {message}")


def main():
    while True:
        message = input("question to your ai agent: ")
        if message == "q":
            break
        print(f"user: {message}")
        messages.append({"role": "user", "content": message})
        call_ai()


if __name__ == "__main__":
    main()
