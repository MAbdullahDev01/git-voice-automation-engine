import os
from dotenv import load_dotenv

load_dotenv()

# Ollama API configuration
OLLAMA_URL = os.getenv("OLLAMA_URL")
MODEL_NAME = os.getenv("MODEL_NAME")

# Voice configuration
VOICE_MODEL_PATH = os.getenv("VOICE_MODEL_PATH")
SPEECH_SPEED = float(os.getenv("SPEECH_SPEED", "1.0"))
SPEECH_VOLUME = float(os.getenv("SPEECH_VOLUME", "1.0"))

# Spotify API configuration
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")