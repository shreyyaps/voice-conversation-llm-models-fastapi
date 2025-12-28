import os
import asyncio
from fastapi import FastAPI, WebSocket
from dotenv import load_dotenv
from deepgram import AsyncDeepgramClient
from deepgram.core.events import EventType
from deepgram.extensions.types.sockets import ListenV2SocketClientResponse

load_dotenv()

app = FastAPI()


class Colors:
    GREEN = '\033[92m'    # 0.90-1.00
    YELLOW = '\033[93m'   # 0.80-0.90
    ORANGE = '\033[91m'   # 0.70-0.80 (using red as orange isn't standard)
    RED = '\033[31m'      # <=0.69
    RESET = '\033[0m'     # Reset to default
def get_confidence_color(confidence: float) -> str:
    """Return the appropriate color code based on confidence score"""
    if confidence >= 0.90:
        return Colors.GREEN
    elif confidence >= 0.80:
        return Colors.YELLOW
    elif confidence >= 0.70:
        return Colors.ORANGE
    else:
        return Colors.RED

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
                msg_type = getattr(message, "type", "Unknown")
                
                if hasattr(message, 'transcript') and message.transcript:
                    print(f"🎤 {message.transcript}")
                    # Show word-level confidence with color coding
                    if hasattr(message, 'words') and message.words:
                        colored_words = []
                        for word in message.words:
                            color = get_confidence_color(word.confidence)
                            colored_words.append(f"{color}{word.word}({word.confidence:.2f}){Colors.RESET}")
                        words_info = " | ".join(colored_words)
                        print(f"  {words_info}")
                elif msg_type == "Connected":
                    print(f" Connected to Deepgram Flux - Ready for audio!")                


        connection.on(EventType.OPEN, lambda _: print("Deepgram connected"))
        connection.on(EventType.MESSAGE, on_message)
        connection.on(EventType.CLOSE, lambda _: print("Deepgram closed"))
        connection.on(EventType.ERROR, lambda e: print("Deepgram error:", e))

        
        listen_task = asyncio.create_task(connection.start_listening())

        try:
            while True:
                audio_chunk = await ws.receive_bytes()

                # Debug: confirm audio is actually flowing
                

                await connection._send(audio_chunk)

        except Exception as e:
            print("Client disconnected:", e)

        finally:
            listen_task.cancel()
            print("Stream ended")
