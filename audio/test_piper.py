import numpy as np
from pathlib import Path
from piper import PiperVoice, SynthesisConfig
import sounddevice as sd
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import SPEECH_SPEED,SPEECH_VOLUME, VOICE_MODEL_PATH

print("Loading Piper model...")

if not VOICE_MODEL_PATH:
    raise ValueError("VOICE_MODEL_PATH is not set. Please check your .env file.")

try:
    voice = PiperVoice.load(VOICE_MODEL_PATH)
    print("Piper model loaded successfully.")
except Exception as e:
    print(f"Error loading Piper model: {e}")
    exit(1)

config = SynthesisConfig(
    length_scale=SPEECH_SPEED,
    volume=SPEECH_VOLUME,
)

def speak_neral(text: str):

    for chunk in voice.synthesize(text, config):
        # Convert the raw 16-bit signed integer bytes into a NumPy array
        audio_data = np.frombuffer(chunk.audio_int16_bytes, dtype=np.int16)
        
        # Convert 16-bit integers (-32768 to 32767) to normalized floats (-1.0 to 1.0)
        audio_float = audio_data.astype(np.float32) / 32768.0
        
        sd.play(audio_float, samplerate=22050)
        sd.wait()