import os

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

def play_music(query: str = ""):
    sp = get_spotify_client()
    if not sp:
        return

    try:
        devices = sp.devices()
        active_device = next((d for d in devices['devices'] if d['is_active']), None)
        
        # If no active device, grab the first available device ID
        device_id = active_device['id'] if active_device else (devices['devices'][0]['id'] if devices['devices'] else None)

        if not device_id:
            print("No Spotify device found. Please open Spotify on your phone or desktop.")
            return

        if query:
            # Search for the track/artist
            results = sp.search(q=query, limit=1, type='track')
            tracks = results.get('tracks', {}).get('items', [])
            
            if not tracks:
                print(f"No tracks found for query: '{query}'")
                return

            track_uri = tracks[0]['uri']
            track_name = tracks[0]['name']
            artist_name = tracks[0]['artists'][0]['name']

            sp.start_playback(device_id=device_id, uris=[track_uri])
            print(f"Now playing: {track_name} by {artist_name}")
        else:
            # Resume current track
            sp.start_playback(device_id=device_id)
            print("Resumed Spotify playback.")

    except Exception as e:
        print(f"Spotify Error: {e}")


def pause_music():
    sp = get_spotify_client()
    if not sp:
        return

    try:
        sp.pause_playback()
        print("Paused Spotify playback.")
    except Exception as e:
        print(f"Spotify Error: {e}")


def skip_track():
    sp = get_spotify_client()
    if not sp:
        return

    try:
        sp.next_track()
        print("Skipped to next track.")
    except Exception as e:
        print(f"Spotify Error: {e}")


def previous_track():
    sp = get_spotify_client()
    if not sp:
        return

    try:
        sp.previous_track()
        print("Playing previous track.")
    except Exception as e:
        print(f"Spotify Error: {e}")