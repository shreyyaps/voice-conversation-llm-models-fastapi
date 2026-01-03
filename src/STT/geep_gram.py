

import os
import asyncio
from deepgram import AsyncDeepgramClient
from deepgram.extensions.types.sockets import ListenV2SocketClientResponse
from deepgram.core.events import EventType
from src.llm_inference.groq import handle_final_transcript




async def geep_gram_ws(ws):
    current_turn_text = ""
    dg = AsyncDeepgramClient(api_key=os.environ["DEEPGRAM_API_KEY"])

    async with dg.listen.v2.connect(
        model="flux-general-en",
        encoding="linear16",
        sample_rate="16000",
    ) as connection:

        def on_message(message: ListenV2SocketClientResponse)-> None:
            nonlocal current_turn_text

            if hasattr(message, "transcript") and message.transcript: # type: ignore
                current_turn_text = message.transcript # type: ignore

            if getattr(message, "type", None) == "TurnInfo":
                if getattr(message, "event", None) == "EndOfTurn":
                    final_text = current_turn_text.strip()

                    if final_text:
                        print(f"\nUser: {final_text}")

                        asyncio.create_task(
                            handle_final_transcript(final_text)
                        )

                    current_turn_text = ""

        connection.on(EventType.OPEN, lambda _: print("Deepgram connected")) # type: ignore
        connection.on(EventType.MESSAGE, on_message)# type: ignore
        connection.on(EventType.CLOSE, lambda _: print("Deepgram closed"))# type: ignore
        connection.on(EventType.ERROR, lambda e: print("Deepgram error:", e))# type: ignore


        asyncio.create_task(connection.start_listening()) # type: ignore

        while True:
            audio_chunk = await ws.receive_bytes()
                

            await connection._send(audio_chunk) # type: ignore