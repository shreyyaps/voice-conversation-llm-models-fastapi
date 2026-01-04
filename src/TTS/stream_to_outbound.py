import asyncio
from fastapi import WebSocket
from src.TTS.eleven_labs import eleven_labs_bytes_streaming

async def stream_to_outbound(ws: WebSocket, text: str):
    queue: asyncio.Queue[bytes | None] = asyncio.Queue()
    loop = asyncio.get_running_loop()

    
    def producer():
        try:
            for chunk in eleven_labs_bytes_streaming(text):
                loop.call_soon_threadsafe(queue.put_nowait, chunk)
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, None)

    loop.run_in_executor(None, producer)

    await ws.send_json({"type": "audio_start"})

    while True:
        chunk = await queue.get()
        if chunk is None:
            break
        await ws.send_bytes(chunk)

    await ws.send_json({"type": "audio_end"})
