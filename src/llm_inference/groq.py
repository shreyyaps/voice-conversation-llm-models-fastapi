
from typing import AsyncIterator

from fastapi import WebSocket
from groq import AsyncGroq

from src.TTS.stream_to_outbound import stream_to_outbound
client = AsyncGroq()


messages = [{"role": "system", "content": "you are a therapist who helps people quit smoking. you name is vina, be supportive, be calm don't be over chatty have normal conversion think like you are speaking not in text don't use (.) fullstop too much use it where ever necessory"}]

async def stream_groq_text(prompt: str, messages: list) -> AsyncIterator[str]:
    messages.append({"role": "user", "content": prompt})

    stream = await client.chat.completions.create(
        model="openai/gpt-oss-20b",
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



async def handle_final_transcript(ws:WebSocket,text: str):
    print("VINI:", end=" ", flush=True)
    buffer = ""
    async for token in stream_groq_text(text, messages):
        print(token, end="", flush=True)
        buffer += token

        
    chunk = buffer.strip()
    await stream_to_outbound(ws,chunk)
    
    buffer = ""

    print("\n")

