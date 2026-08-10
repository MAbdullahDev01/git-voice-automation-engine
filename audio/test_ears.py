import speech_recognition as sr
import keyboard as k
import time

from utils.logger import get_logger
from audio.test_piper import speak_neral

# Logging
logger = get_logger(__name__)


def listen_neural() -> str:
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    print("\nJarvis: Hold 'M' to speak...")

    while not k.is_pressed("m"):
        time.sleep(0.05)
        
    print("Jarvis: Listening... (Release 'M' to finish)")

    k.block_key("m")
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.1)
            
            audio_chunks = []
            stream = mic.stream
            
            while k.is_pressed('m'):
                try:
                    chunk = stream.read(source.CHUNK)
                    audio_chunks.append(chunk)
                except IOError:
                    continue
    finally:
        k.unblock_key("m")
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