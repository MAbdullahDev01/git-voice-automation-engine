import speech_recognition as sr

def listen_neural():
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as mic:
            recognizer.adjust_for_ambient_noise(mic, duration=0.2)
            print("Jarvis: Listening...")
            audio = recognizer.listen(mic, timeout=5, phrase_time_limit=8)
    except sr.WaitTimeoutError:
        print("Jarvis: No speech detected.")
        return ""

    try:
        return recognizer.recognize_google(audio) # type: ignore
    except sr.UnknownValueError:
        print("Jarvis: I did not catch that.")
        return ""
    except sr.RequestError:
        print("Jarvis: Speech recognition is unavailable.")
        return ""