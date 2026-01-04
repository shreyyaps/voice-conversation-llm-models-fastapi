# test_elevenlabs_stream.py
from dotenv import load_dotenv
load_dotenv()

from elevenlabs import stream
from elevenlabs.client import ElevenLabs
import os
client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY")
)

audio_stream = client.text_to_speech.stream(
    text="Hello Shreyash, this is a streaming test from Eleven Labs.",
    voice_id="XrExE9yKIg1WjnnlVkGX",
    model_id="eleven_turbo_v2_5",
    output_format="pcm_16000",
)

print("audio_stream type:", type(audio_stream))
print("Iterating over stream...\n")

count = 0

for chunk in audio_stream:
    print(
        f"chunk {count}:",
        type(chunk),
        len(chunk) if isinstance(chunk, bytes) else chunk
    )
    count += 1

print("\nDONE. Total chunks:", count)
