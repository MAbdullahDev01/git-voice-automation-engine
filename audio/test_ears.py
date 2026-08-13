import time

import keyboard as k
import speech_recognition as sr

from utils.logger import get_logger

# Logging
logger = get_logger(__name__)


def listen_neural(stop_key: str = "m", stop_on_release: bool = True, stop_event=None) -> str:
    """Capture microphone audio until the stop key is released or stop_event is set.

    The key polling is intentionally non-blocking; the caller may run this in a worker
    thread rather than on the GUI event loop.
    """
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    audio_chunks = []

    print(f"\nJarvis: Hold '{stop_key.upper()}' to speak...")

    while not k.is_pressed(stop_key):
        if stop_event is not None and stop_event.is_set():
            return ""
        time.sleep(0.05)

    print(f"Jarvis: Listening... (Release '{stop_key.upper()}' to finish)")

    k.block_key(stop_key)
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.1)
            stream = mic.stream

            while True:
                if stop_event is not None and stop_event.is_set():
                    break
                if stop_on_release and not k.is_pressed(stop_key):
                    break
                try:
                    chunk = stream.read(source.CHUNK)
                    audio_chunks.append(chunk)
                except IOError:
                    continue
    finally:
        k.unblock_key(stop_key)

    print("Jarvis: Processing transcription...")

    if not audio_chunks:
        return ""

    raw_audio_bytes = b"".join(audio_chunks)
    audio_data = sr.AudioData(raw_audio_bytes, source.SAMPLE_RATE, source.SAMPLE_WIDTH)

    try:
        return recognizer.recognize_google(audio_data).strip()
    except sr.UnknownValueError:
        logger.error("Speech recognition did not catch the input")
        return ""
    except sr.RequestError as exc:
        logger.error("Speech recognition service is unavailable: %s", exc)
        return ""