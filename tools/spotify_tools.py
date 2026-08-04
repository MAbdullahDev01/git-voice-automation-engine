from rapidfuzz import fuzz
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI

SPOTIFY_SCOPES = [
    "user-modify-playback-state",
    "user-read-playback-state",
    "user-read-currently-playing"
]

def get_spotify_client():
    if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET:
        print("Missing Spotify API credentials in .env file.")
        return None

    try:
        sp = Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope=" ".join(SPOTIFY_SCOPES),
            open_browser=True
        ))
        return sp
    except Exception as e:
        print(f"Error authenticating with Spotify: {e}")
        return None

def play_music(query: str, market: str = "PK") -> str:
    sp = get_spotify_client()
    if not sp:
        return "Spotify client not available."

    if not query.strip():
        return "No track specified to play."

    try:
        results = sp.search(q=query, type="track", limit=10, market=market) or {}
        tracks = (results.get("tracks") or {}).get("items", [])

        if not tracks:
            return f"Couldn't find any track matching '{query}' on Spotify."

        def score(track):
            combined = f"{track['name']} {track['artists'][0]['name']}".lower()
            return fuzz.token_set_ratio(query.lower(), combined)

        best = max(tracks, key=score)

        # Sanity check - avoid confidently playing a poor match.
        if score(best) < 55:
            return f"Couldn't find a confident match for '{query}' on Spotify."

        sp.start_playback(uris=[best["uri"]])
        return f"Playing {best['name']} by {best['artists'][0]['name']}."

    except Exception as e:
        print(f"Spotify API Exception: {e}")
        return f"Failed to play music on Spotify: {e}"


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


def pause_music():
    sp = get_spotify_client()
    if not sp:
        return "Spotify client not available."

    try:
        sp.pause_playback()
        return "Paused Spotify playback."
    except Exception as e:
        return f"Spotify Error: {e}"


def skip_track():
    sp = get_spotify_client()
    if not sp:
        return "Spotify client not available."

    try:
        sp.next_track()
        return "Skipped to next track."
    except Exception as e:
        return f"Spotify Error: {e}"


def previous_track():
    sp = get_spotify_client()
    if not sp:
        return "Spotify client not available."

    try:
        sp.previous_track()
        return "Playing previous track."
    except Exception as e:
        return f"Spotify Error: {e}"

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
        print(f"Spotify Error: {e}")
        return "Error retrieving current playing information."