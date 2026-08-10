# Imports
from rapidfuzz import fuzz
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from utils.logger import get_logger

# Importing configuration variables from the config
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI

# Logging
logger = get_logger(__name__)

# Defining the required Spotify scopes for the application
SPOTIFY_SCOPES = [
    "user-modify-playback-state",
    "user-read-playback-state",
    "user-read-currently-playing"
]

_spotify_client = None

# Create a Spotify client using the Spotipy library
def get_spotify_client():
    global _spotify_client
    if _spotify_client is not None:
        return _spotify_client
    
    if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET:
        print("Missing Spotify API credentials in .env file.")
        return None

    try:
        _spotify_client = Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope=" ".join(SPOTIFY_SCOPES),
            open_browser=True
        ))
        return _spotify_client
    except Exception as e:
        logger.error(f"Error authenticating with Spotify: {e}")
        return None

# =================================
# Spotify tools
# =================================

# Get current playing track information function
def get_current_playing_info():
    sp = get_spotify_client()
    if not sp:
        return "Spotify client not available."

    try:
        current_playback = sp.current_playback()
        if not current_playback or not current_playback.get('item'):
            return "No track is currently playing."

        track = current_playback['item']
        track_name = track['name']
        artist_name = ', '.join(artist['name'] for artist in track['artists'])
        album_name = track['album']['name']

        return f"Currently playing: '{track_name}' by {artist_name} from the album '{album_name}'."
    except Exception as e:
        logger.error(f"Spotify Error: {e}")
        return "Error retrieving current playing information."

# Pause music function
def pause_music():
    sp = get_spotify_client()
    if not sp:
        return "Spotify client not available."

    try:
        sp.pause_playback()
        return "Paused Spotify playback."
    except Exception as e:
        logger.error(f"Spotify Error: {e}")
        return f"Spotify Error: {e}"

# Play music function
def play_music(query: str, market: str = "PK") -> str:
    if not query.strip():
        return "No track specified to play."
    return play_music_smart(query, query, market=market)

# Smarter play music function that uses fuzzy matching to find the best track
def play_music_smart(raw_query: str, corrected_query: str, market: str = "PK") -> str:
    sp = get_spotify_client()
    if not sp:
        return "Spotify client not available."

    candidates = []
    for q in {raw_query, corrected_query}:
        if not q.strip():
            continue
        res = sp.search(q=q, type="track", limit=5, market=market) or {}
        candidates += (res.get("tracks") or {}).get("items", [])

    if not candidates:
        return f"Couldn't find any track matching '{raw_query}' on Spotify."

    def score(track):
        combined = f"{track['name']} {track['artists'][0]['name']}".lower()
        return max(
            fuzz.token_set_ratio(raw_query.lower(), combined),
            fuzz.token_set_ratio(corrected_query.lower(), combined),
        )

    best = max(candidates, key=score)
    if score(best) < 55:
        return f"Couldn't find a confident match for '{raw_query}' on Spotify."

    sp.start_playback(uris=[best["uri"]])
    return f"Playing {best['name']} by {best['artists'][0]['name']}."

# Play previous track function
def previous_track():
    sp = get_spotify_client()
    if not sp:
        return "Spotify client not available."

    try:
        sp.previous_track()
        return "Playing previous track."
    except Exception as e:
        logger.error(f"Spotify Error: {e}")
        return f"Spotify Error: {e}"

# Skip to next track function
def skip_track():
    sp = get_spotify_client()
    if not sp:
        return "Spotify client not available."

    try:
        sp.next_track()
        return "Skipped to next track."
    except Exception as e:
        logger.error(f"Spotify Error: {e}")
        return f"Spotify Error: {e}"