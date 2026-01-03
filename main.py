from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, WebSocket
from src.STT.geep_gram import geep_gram_ws



app = FastAPI()

@app.websocket("/ws/audio")
async def audio_ws(ws: WebSocket):
    await ws.accept()

    try:
        await geep_gram_ws(ws)
    except Exception as e:
        print("Client disconnected:", e)



