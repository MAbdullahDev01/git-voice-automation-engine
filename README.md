# Git Voice Automation Engine

This project is a voice-first local assistant that lets you interact with an Ollama-backed language model through either typed text or microphone input. The application listens for your voice, sends the prompt to the model, and speaks the reply back using a Piper text-to-speech voice model.

Over time, the project has grown into a small personal automation prototype with:

- speech recognition for voice input
- text-to-speech output with adjustable speed and volume
- an Ollama-powered assistant loop
- Git automation helpers that can generate and run commit messages

It is designed as a simple demo/experiment for combining:

- speech recognition
- a local or remote LLM via Ollama
- text-to-speech output
- Git workflow automation
- a small command loop in Python

## What this project does

When you run the app:

1. You can type a message and press Enter.
2. Or you can press and hold M to speak into your microphone.
3. The app sends your input to Ollama.
4. The model generates a reply.
5. The reply is printed in the console and spoken aloud.

Typing `quit` exits the program.

## Repository structure

```text
.
├── main.py                 # Main entry point and interactive loop
├── config.py               # Loads environment variables from .env
├── .env                    # Local environment settings (not committed)
├── .python-version         # Python version used by the project
├── LICENSE                 # Project license
├── README.md               # Project overview and usage guide
├── utils/
│   ├── jarvis.py           # Sends prompts to Ollama
│   ├── test_ears.py        # Microphone capture and speech-to-text
│   └── test_piper.py       # Text-to-speech playback with Piper
│   └── git_utils.py        # Git automation helpers for commit generation
├── voice_models/
│   └── en_GB-alan-medium.onnx
│       └── en_GB-alan-medium.onnx.json
└── venv/                   # Local virtual environment
```

## Main files

- `main.py`
  - Starts the interactive loop.
  - Accepts typed input or voice input.
  - Prints and speaks the assistant response.

- `config.py`
  - Loads environment variables from `.env`.
  - Includes voice and model settings.

- `utils/jarvis.py`
  - Sends the prompt to the configured Ollama API endpoint.

- `utils/test_ears.py`
  - Captures microphone audio and transcribes it using Google Speech Recognition.

- `utils/test_piper.py`
  - Synthesizes speech using the included Piper voice model.
  - Uses the configured speed and volume settings.

- `utils/git_utils.py`
  - Adds Git automation features such as generating a commit message from the staged diff and optionally committing/pushing changes.

## Requirements

This project depends on Python packages such as:

- `requests`
- `python-dotenv`
- `speechrecognition`
- `keyboard`
- `numpy`
- `sounddevice`
- `piper` (or the relevant Piper runtime dependency used by your environment)

You will also need:

- a working microphone and speakers/headphones
- an Ollama instance running locally or a reachable Ollama endpoint
- a model installed in Ollama, such as `llama3.2` or another supported model

## Setup

1. Create and activate a virtual environment:

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install the required dependencies:

```powershell
pip install requests python-dotenv SpeechRecognition keyboard numpy sounddevice
```

If your environment needs the Piper package separately, install it according to your local setup.

3. Create a `.env` file in the project root with your Ollama settings:

```env
OLLAMA_URL=http://localhost:11434/api/chat
MODEL_NAME=llama3.2
VOICE_MODEL_PATH=./voice_models/en_GB-alan-medium.onnx
SPEECH_SPEED=0.80
SPEECH_VOLUME=1.0
```

If you use a different Ollama host or port, update the URL accordingly. The speech settings can be tuned to make the assistant speak faster or slower.

4. Make sure Ollama is running and that your chosen model is available.

## How to run

From the project root:

```powershell
python main.py
```

Once it starts, you can:

- type a prompt and press Enter
- or press and hold `M` to speak

To exit the app, type:

```text
quit
```

## Notes and limitations

- Voice input uses Google speech recognition, so network access may be required.
- The text-to-speech experience depends on the local audio environment and the Piper model files in the `voice_models` directory.
- The Git helper workflow is a convenience feature and should be used carefully, especially when pushing changes automatically.
- The project is intentionally lightweight and is meant as a practical example rather than a production-grade voice assistant framework.

## Recent progress

The project now includes:

- configurable speech speed and volume settings
- a working voice-driven assistant loop
- a Git helper module that can generate commit messages from staged changes
- a cleaner project structure with dedicated utility code

## Future ideas

Possible next improvements include:

- adding better command handling and conversation memory
- supporting more local speech-to-text options
- improving safety checks around automatic Git commits and pushes
- expanding the assistant into a broader automation workflow
- adding commands to play name specific songs on spotify desktop
