import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
VOICE_MODEL_PATH = os.getenv("VOICE_MODEL_PATH")
SPEECH_SPEED = float(os.getenv("SPEECH_SPEED", "1.0"))
SPEECH_VOLUME = float(os.getenv("SPEECH_VOLUME", "1.0"))