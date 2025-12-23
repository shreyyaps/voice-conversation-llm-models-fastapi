

from os import write
import time
from fastapi import FastAPI, WebSocket
import numpy as np

app = FastAPI()

@app.websocket('ws/audio')
async def audio_ws(ws: WebSocket):
    await ws.accept()
    print('client connected to websocket')
    audio_bytes = bytearray()
    try:
        while True:
            data = await ws.receive_bytes()
            audio_bytes.extend(data)
            print(f'recieved {len(data)} bytes---')

    except Exception:
        print('disconnected')

    pcm16 = np.frombuffer(audio_bytes, dtype=np.int16)

    write(f'{time.time()}.wav', 16000, pcm16) # type: ignore
    print('file saved')
