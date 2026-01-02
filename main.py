import os
import asyncio
from fastapi import FastAPI, WebSocket
from dotenv import load_dotenv
from deepgram import AsyncDeepgramClient
from deepgram.core.events import EventType
from deepgram.extensions.types.sockets import ListenV2SocketClientResponse

load_dotenv()
from src.llm_inference.groq import handle_final_transcript


app = FastAPI()


@app.websocket("/ws/audio")
async def audio_ws(ws: WebSocket):
    await ws.accept()

    messages = [{"role": "system", "content": "you are a therapist who helps people quit smoking. you name is vina, be supportive, be calm don't be over chatty have normal conversion think like you are speaking not in text"}]
    current_turn_text = ""
    print("Client connected")

    dg = AsyncDeepgramClient(api_key=os.environ["DEEPGRAM_API_KEY"])

    async with dg.listen.v2.connect(
        model="flux-general-en",
        encoding="linear16",
        sample_rate="16000",
        
    ) as connection:

        def on_message(message: ListenV2SocketClientResponse) -> None:
                nonlocal current_turn_text

                # Regular transcript updates i need to add show on my one straming to the frontend.
                if hasattr(message, "transcript") and message.transcript: # type: ignore
                    current_turn_text = message.transcript # type: ignore
                    

                # Turn boundary detection 
                if getattr(message, "type", None) == "TurnInfo":
                    if getattr(message, "event", None) == "EndOfTurn":
                        final_text = current_turn_text.strip()

                        if final_text:
                            print(f"\nyou: {final_text}")

                            # THIS is where i call the LLM
                            
                            asyncio.create_task(
                            handle_final_transcript(final_text, messages)
                            )

                        current_turn_text = ""              


        connection.on(EventType.OPEN, lambda _: print("Deepgram connected"))
        connection.on(EventType.MESSAGE, on_message)
        connection.on(EventType.CLOSE, lambda _: print("Deepgram closed"))
        connection.on(EventType.ERROR, lambda e: print("Deepgram error:", e))

        
        asyncio.create_task(connection.start_listening())

        try:
            while True:
                audio_chunk = await ws.receive_bytes()
                

                await connection._send(audio_chunk)

        except Exception as e:
            print("Client disconnected:", e)
