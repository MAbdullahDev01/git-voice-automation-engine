from curses.ascii import SP
import os
from re import S
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
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")