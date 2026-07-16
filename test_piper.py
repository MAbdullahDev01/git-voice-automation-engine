import numpy as np
from piper import PiperVoice, SynthesisConfig
import sounddevice as sd

model_path = "./voice_models/en_GB-alan-medium.onnx"
print("Loading Piper model...")
voice = PiperVoice.load(model_path)
config = SynthesisConfig(
    length_scale= 1.0,
    volume= 1.0,
)

def speak_neral(text: str):

    for chunk in voice.synthesize(text, config):
        # Convert the raw 16-bit signed integer bytes into a NumPy array
        audio_data = np.frombuffer(chunk.audio_int16_bytes, dtype=np.int16)
        
        # Convert 16-bit integers (-32768 to 32767) to normalized floats (-1.0 to 1.0)
        audio_float = audio_data.astype(np.float32) / 32768.0
        
        sd.play(audio_float, samplerate=22050)
        sd.wait()