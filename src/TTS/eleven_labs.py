import asyncio
import os
from typing import IO
from io import BytesIO
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
load_dotenv()

elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"),)


def eleven_labs_bytes_streaming(text: str) -> IO[bytes]:
    response = elevenlabs.text_to_speech.stream(
        voice_id="XrExE9yKIg1WjnnlVkGX", 
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",
        # Optional voice settings that allow you to customize the output
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
            speed=1.0,
        ),
    )
    # Create a BytesIO object to hold the audio data in memory
    audio_stream = BytesIO()
    # Write each chunk of audio data to the stream
    for chunk in response:
        if chunk:
            audio_stream.write(chunk)
    # Reset stream position to the beginning
    audio_stream.seek(0)
    # Return the stream for further use
    play(audio_stream)
    return audio_stream




async def async_eleven_labs_bytes_streaming(text: str) -> IO[bytes]:
    return await asyncio.to_thread(eleven_labs_bytes_streaming, text)
