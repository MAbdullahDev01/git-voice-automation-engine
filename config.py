import os
from dotenv import load_dotenv

load_dotenv()

# # Ollama API configuration
# OLLAMA_URL = os.getenv("OLLAMA_URL")
# MODEL_NAME = os.getenv("MODEL_NAME")

# Groq API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_FAST_MODEL = os.getenv("GROQ_FAST_MODEL")
GROQ_SMART_MODEL = os.getenv("GROQ_SMART_MODEL")

# Voice configuration
VOICE_MODEL_PATH = os.getenv("VOICE_MODEL_PATH")
SPEECH_SPEED = float(os.getenv("SPEECH_SPEED", "1.0"))
SPEECH_VOLUME = float(os.getenv("SPEECH_VOLUME", "1.0"))

# Spotify API configuration
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")