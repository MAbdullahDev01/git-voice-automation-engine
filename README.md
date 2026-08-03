# Git Voice Automation Engine

Git Voice Automation Engine is a voice-first assistant and automation demo built in Python. It combines typed input, push-to-talk speech input, text-to-speech output, Groq-powered chat, Git automation helpers, and Spotify playback controls in a single local app.

## What It Does

When you run the app, it can:

1. Accept typed text in the terminal.
2. Accept voice input by pressing Enter in CLI mode and holding `M` while speaking.
3. Route your request into one of several intents, including general chat, Git branch actions, Git commits, and Spotify playback commands.
4. Speak the response back through the included Piper voice model.

The project currently supports both a terminal CLI and a PyQt6 window UI.

## Repository Structure

```text
.
├── app.py
├── config.py
├── main.py
├── requirements.txt
├── audio/
│   ├── __init__.py
│   ├── test_ears.py
│   └── test_piper.py
├── core/
│   ├── __init__.py
│   ├── jarvis.py
│   ├── router.py
│   └── schemas.py
├── tools/
│   ├── __init__.py
│   ├── git_tools.py
│   └── spotify_tools.py
├── utils/
│   ├── groq.py
│   └── helpers.py
└── voice_models/
    ├── en_GB-alan-medium.onnx
    └── en_GB-alan-medium.onnx.json
```

## Main Components

- `main.py` starts the app, handles CLI mode, and routes text or voice input through the assistant pipeline.
- `app.py` provides the PyQt6 window interface.
- `core/router.py` classifies user input into intents such as chat, Git, or Spotify actions.
- `core/jarvis.py` sends general chat prompts to Groq.
- `tools/git_tools.py` handles branch creation, switching, deletion, listing, and commit generation.
- `tools/spotify_tools.py` connects to Spotify playback controls through Spotipy.
- `audio/test_ears.py` captures microphone input and uses Google speech recognition.
- `audio/test_piper.py` speaks responses using the local Piper voice model.

## Requirements

You will need:

- Python 3.12 or newer
- a working microphone and speakers or headphones
- a Groq API key
- optional Spotify developer credentials if you want Spotify commands
- the included Piper voice model files in `voice_models/`

The project uses packages such as:

- `groq`
- `pydantic`
- `python-dotenv`
- `SpeechRecognition`
- `keyboard`
- `numpy`
- `sounddevice`
- `piper-tts`
- `PyQt6`
- `spotipy`

## Setup

1. Create and activate a virtual environment:

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create a `.env` file in the project root. A good starting point is:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_FAST_MODEL=llama-3.1-8b-instant
GROQ_SMART_MODEL=llama-3.3-70b-versatile
VOICE_MODEL_PATH=./voice_models/en_GB-alan-medium.onnx
SPEECH_SPEED=0.80
SPEECH_VOLUME=1.0
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8080/callback
```

If you are not using Spotify, you can leave the Spotify settings unset.

## How To Use It

### Terminal CLI

Run the CLI mode with:

```powershell
python main.py --cli
```

Then:

- type a prompt and press Enter to send it as text
- press Enter on an empty line to start push-to-talk voice input
- hold `M` while speaking, then release `M` to finish recording
- type `quit`, `exit`, or `bye` to close the app

Examples:

- `What does this repo do?`
- `create a git branch called feature/voice-ui`
- `commit the staged changes`
- `play reflections by the neighbourhood`
- `pause music`

### Window UI

Run the window UI with:

```powershell
python main.py --window
```

If `PyQt6` is installed, the window UI is the default when you run `python main.py` without arguments. The window uses the same assistant pipeline as the CLI.

### Git Commands

Git-related prompts are routed automatically. The app can:

- create a new branch
- switch branches
- delete a branch
- list local branches
- show the current branch
- generate a commit message from the staged diff
- commit and push after confirmation

For commit flow, the app stages changes, generates a conventional commit message, and then asks for confirmation before committing and pushing.

### Spotify Commands

Spotify playback works through your authenticated Spotify account and an active device. Supported prompts include:

- play a track or resume playback
- pause playback
- skip to the next track
- return to the previous track

## Notes

- Voice input uses Google speech recognition, so network access may be required.
- The Piper voice model must exist at the path defined in `VOICE_MODEL_PATH`.
- The Git automation helpers can commit and push changes, so use them carefully.
- Spotify commands require valid Spotify API credentials and an active playback device.

## Future Ideas

Possible next improvements include:

- expanding the command router with more intents
- adding safer commit confirmation flows
- improving offline speech-to-text options
- adding richer memory and follow-up handling
- expanding Spotify support with more playback commands
