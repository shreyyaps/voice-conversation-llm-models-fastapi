
from typing import AsyncIterator

from groq import AsyncGroq

from src.TTS.eleven_labs import async_eleven_labs_bytes_streaming, eleven_labs_bytes_streaming
client = AsyncGroq()


messages = [{"role": "system", "content": "you are a therapist who helps people quit smoking. you name is vina, be supportive, be calm don't be over chatty have normal conversion think like you are speaking not in text don't use (.) fullstop too much use it where ever necessory"}]

async def stream_llama_text(prompt: str, messages: list) -> AsyncIterator[str]:
    messages.append({"role": "user", "content": prompt})

    stream = await client.chat.completions.create(
        model="moonshotai/kimi-k2-instruct-0905",
        messages=messages,
        stream=True,
    )

    assistant_text = ""

    async for chunk in stream:
        token = chunk.choices[0].delta.content
        if token:
            assistant_text += token
            yield token

    
    messages.append({"role": "assistant", "content": assistant_text})

DELIMITERS = ( "?", "!")

async def handle_final_transcript(text: str, messages: list):
    print("VINI:", end=" ", flush=True)

    buffer = ""

    async for token in stream_llama_text(text, messages):
        print(token, end="", flush=True)
        buffer += token

        if buffer.strip().endswith(DELIMITERS):
            chunk = buffer.strip()
            await async_eleven_labs_bytes_streaming(chunk)
            buffer = ""

    print("\n")

