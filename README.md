# Git Voice Automation Engine

This project is a voice-first local assistant that lets you interact with an Ollama-backed language model through either typed text or microphone input. The application listens for your voice, sends the prompt to the model, and speaks the reply back using a Piper text-to-speech voice model.

It is designed as a simple demo/experiment for combining:

- speech recognition
- a local or remote LLM via Ollama
- text-to-speech output
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
├── tools/
│   ├── jarvis.py           # Sends prompts to Ollama
│   ├── test_ears.py        # Microphone capture and speech-to-text
│   ├── test_piper.py       # Text-to-speech playback with Piper
│   └── git_tools.py        # Placeholder file for future Git-related helpers
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
  - Loads `OLLAMA_URL` and `MODEL_NAME` from a `.env` file.

- `tools/jarvis.py`
  - Sends the prompt to the configured Ollama API endpoint.

- `tools/test_ears.py`
  - Captures microphone audio and transcribes it using Google Speech Recognition.

- `tools/test_piper.py`
  - Synthesizes speech using the included Piper voice model.

- `tools/git_tools.py`
  - Currently empty and can be used for future Git automation work.

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
```

If you use a different Ollama host or port, update the URL accordingly.

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
- The project is intentionally lightweight and is meant as a practical example rather than a production-grade voice assistant framework.

## Future ideas

Possible next improvements include:

- adding better command handling and conversation memory
- supporting more local speech-to-text options
- adding Git automation helpers in `tools/git_tools.py`
- improving error handling and startup checks
