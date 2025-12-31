import os
from typing import Iterator

from groq import Groq
client = Groq()

def stream_llama_text(prompt: str) -> Iterator[str]: # type: ignore
    stream = client.chat.completions.create(
         model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    for chunk in stream:
        token = chunk.choices[0].delta.content
        if token:
            yield token


def handle_final_transcript(text: str):
    print("AI:", end=" ", flush=True)

    for token in stream_llama_text(text):
        print(token, end="", flush=True)

    print("\n")


