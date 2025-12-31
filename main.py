import os
import asyncio
from fastapi import FastAPI, WebSocket
from dotenv import load_dotenv
load_dotenv()
from deepgram import AsyncDeepgramClient
from deepgram.core.events import EventType
from deepgram.extensions.types.sockets import ListenV2SocketClientResponse


from llm_inference.groq import handle_final_transcript

app = FastAPI()




@app.websocket("/ws/audio")
async def audio_ws(ws: WebSocket):
    await ws.accept()
    print("Client connected")

    dg = AsyncDeepgramClient(api_key=os.environ["DEEPGRAM_API_KEY"])

    async with dg.listen.v2.connect(
        model="flux-general-en",
        encoding="linear16",
        sample_rate="16000",
        
    ) as connection:

        def on_message(message: ListenV2SocketClientResponse) -> None:
            global last_partial

            msg_type = getattr(message, "type", None)

            if msg_type == "Connected":
                print("Connected to Deepgram Flux - Ready for audio!")
                return

            if not hasattr(message, "transcript"):
                return

            transcript = message.transcript # type: ignore
            if not transcript:
                return

            
            if not message.is_final: # type: ignore
                if transcript.startswith(last_partial): # type: ignore
                    new_text = transcript[len(last_partial):] # type: ignore
                else:
                    # safety fallback (rare but possible)
                    new_text = transcript

                print(new_text, end="", flush=True)
                last_partial = transcript
                return

            
            print()  # newline after typing
            print(f"FINAL: {transcript}")
            last_partial = ""  # reset for next utterance

            handle_final_transcript(transcript)              


        connection.on(EventType.OPEN, lambda _: print("Deepgram connected"))
        connection.on(EventType.MESSAGE, on_message)
        connection.on(EventType.CLOSE, lambda _: print("Deepgram closed"))
        connection.on(EventType.ERROR, lambda e: print("Deepgram error:", e))

        
        listen_task = asyncio.create_task(connection.start_listening())

        try:
            while True:
                # cute step 1 get the mf bytes (thank god to web audio API to send exact format)
                audio_chunk = await ws.receive_bytes()
                # cute step 2 need to send those bytes to deepgram
                await connection._send(audio_chunk)

        except Exception as e:
            print("Client disconnected:", e)

        finally:
            listen_task.cancel()
            print("Stream ended")
