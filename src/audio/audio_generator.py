import asyncio
from google import genai
from google.genai import types
from config import settings
import wave
import queue
import logging
import gradio as gr
import io
import time

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.gemini_api_key.get_secret_value(), http_options={'api_version': 'v1alpha'})

async def generate_music(user_hash: str, music_tone: str, receive_audio):
      async with (
        client.aio.live.music.connect(model='models/lyria-realtime-exp') as session,
        asyncio.TaskGroup() as tg,
      ):
        # Set up task to receive server messages.
        tg.create_task(receive_audio(session, user_hash))

        # Send initial prompts and config
        await session.set_weighted_prompts(
          prompts=[
            types.WeightedPrompt(text=music_tone, weight=1.0),
          ]
        )
        await session.set_music_generation_config(
          config=types.LiveMusicGenerationConfig(bpm=90, temperature=1.0)
        )
        await session.play()
        logger.info(f"Started music generation for user hash {user_hash}, music tone: {music_tone}")
        await cleanup_music_session(user_hash)
        sessions[user_hash] = {
            'session': session,
            'queue': queue.Queue(maxsize=3)
        }
        
async def change_music_tone(user_hash: str, new_tone):
    logger.info(f"Changing music tone to {new_tone}")
    session = sessions.get(user_hash, {}).get('session')
    if not session:
        logger.error(f"No session found for user hash {user_hash}")
        return
    await session.reset_context()
    await session.set_weighted_prompts(
        prompts=[types.WeightedPrompt(text=new_tone, weight=1.0)]
    )
        

SAMPLE_RATE = 48000
NUM_CHANNELS = 2  # Stereo
SAMPLE_WIDTH = 2  # 16-bit audio -> 2 bytes per sample

async def receive_audio(session, user_hash):
    """Process incoming audio from the music generation."""
    while True:
        try:
            async for message in session.receive():
                if message.server_content and message.server_content.audio_chunks:
                    audio_data = message.server_content.audio_chunks[0].data
                    queue = sessions[user_hash]['queue']
                    # audio_data is already bytes (raw PCM)
                    await asyncio.to_thread(queue.put, audio_data)
                await asyncio.sleep(10**-12)
        except Exception as e:
            logger.error(f"Error in receive_audio: {e}")
            break

sessions = {}

async def start_music_generation(user_hash: str, music_tone: str):
    """Start the music generation in a separate thread."""
    await generate_music(user_hash, music_tone, receive_audio)
    
async def cleanup_music_session(user_hash: str):
    if user_hash in sessions:
        logger.info(f"Cleaning up music session for user hash {user_hash}")
        session = sessions[user_hash]['session']
        await session.stop()
        await session.close()
        del sessions[user_hash]
    

def update_audio(user_hash):
    """Continuously stream audio from the queue as WAV bytes."""
    while True:
        if user_hash not in sessions:
            time.sleep(0.5)
            continue
        queue = sessions[user_hash]['queue']
        pcm_data = queue.get() # This is raw PCM audio bytes
        
        if not isinstance(pcm_data, bytes):
            logger.warning(f"Expected bytes from audio_queue, got {type(pcm_data)}. Skipping.")
            continue

        # Lyria provides stereo, 16-bit PCM at 48kHz.
        # Ensure the number of bytes is consistent with stereo 16-bit audio.
        # Each frame = NUM_CHANNELS * SAMPLE_WIDTH bytes.
        # If len(pcm_data) is not a multiple of (NUM_CHANNELS * SAMPLE_WIDTH), 
        # it might indicate an incomplete chunk or an issue.
        bytes_per_frame = NUM_CHANNELS * SAMPLE_WIDTH
        if len(pcm_data) % bytes_per_frame != 0:
            logger.warning(
                f"Received PCM data with length {len(pcm_data)}, which is not a multiple of "
                f"bytes_per_frame ({bytes_per_frame}). This might cause issues with WAV formatting."
            )
            # Depending on strictness, you might want to skip this chunk:
            # continue 

        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(NUM_CHANNELS)
            wf.setsampwidth(SAMPLE_WIDTH) # Corresponds to 16-bit audio
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(pcm_data)
        wav_bytes = wav_buffer.getvalue()
        yield wav_bytes