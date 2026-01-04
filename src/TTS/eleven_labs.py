import os
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
load_dotenv()
elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

def eleven_labs_bytes_streaming(text: str):
    response = elevenlabs.text_to_speech.stream(
        voice_id="XrExE9yKIg1WjnnlVkGX",
        output_format="pcm_16000",
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
            speed=1.0,
        ),
    )

    count = 0
    for chunk in response:
        if isinstance(chunk, bytes):
            count += 1
            #print(f"EL chunk {count}: {len(chunk)} bytes")
            yield chunk
