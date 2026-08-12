# J.A.R.V.I.S — Git Voice Automation Engine

A voice-first, LLM-powered desktop assistant for Python developers. JARVIS routes natural language (typed or spoken) into structured intents — general conversation, Git automation, or Spotify playback control — and responds through a live-streaming, typewriter-style desktop UI or a terminal CLI, with optional text-to-speech output.

Built around a Groq-hosted LLM pipeline with strict JSON-schema structured outputs, a confidence-gated intent router, rolling conversational memory, and a frameless PyQt6 HUD interface.

---

## Table of Contents

- [J.A.R.V.I.S — Git Voice Automation Engine](#jarvis--git-voice-automation-engine)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Architecture](#architecture)
  - [Repository Structure](#repository-structure)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Usage](#usage)
    - [Desktop UI (default)](#desktop-ui-default)
    - [Terminal CLI](#terminal-cli)
  - [Supported Intents](#supported-intents)
  - [How Routing Works](#how-routing-works)
  - [Memory](#memory)
  - [Spotify Integration](#spotify-integration)
  - [Git Automation](#git-automation)
  - [Roadmap](#roadmap)
  - [Contributing](#contributing)
  - [License](#license)

---

## Features

- **Natural language intent routing** — a Groq LLM classifies free-form input into a strict intent schema (`git_commit`, `spotify_play`, `general_chat`, etc.) with a confidence score, using `json_schema` strict-mode structured outputs.
- **Deterministic fast-path routing** — unambiguous commands (`pause`, `skip`, `current branch`, ...) are matched with regex before ever touching the LLM, for near-zero latency.
- **Confidence-gated fallback** — low-confidence classifications automatically fall back to `general_chat` instead of risking an unintended action.
- **Streaming chat responses** — general conversation streams token-by-token to the terminal, the desktop UI, and a sentence-level text-to-speech queue simultaneously.
- **Voice input & output** — push-to-talk microphone capture (Google Speech Recognition) and local neural TTS via Piper.
- **Rolling conversational memory** — recent turns are kept verbatim; older turns are collapsed into a compact LLM-generated summary and persisted to disk as JSON.
- **Git automation** — AI-generated Conventional Commit messages from the staged diff, plus branch create/switch/delete/list, with a confirm-before-push safety step.
- **Spotify playback control** — play, pause, skip, previous, and "what's playing" commands, with fuzzy-matched search (via `rapidfuzz`) across raw and LLM-corrected queries to handle imperfect transliteration/STT output.
- **Animated desktop HUD** — a frameless, custom-painted PyQt6 window with a state-reactive glowing HUD widget (idle / listening / processing / speaking / error), draggable title bar, and live-streaming chat log.

---

## Architecture

```
                ┌─────────────────────┐
   Typed text   │                     │
   or voice ──▶ │   main.py pipeline  │
                │  (process_pipeline) │
                └─────────┬───────────┘
                          │
                 ┌────────▼─────────┐
                 │  core/router.py  │  deterministic regex pass
                 │  (intent + query │  → Groq structured output
                 │   + confidence)  │  → confidence gate
                 └────────┬─────────┘
                          │
        ┌─────────────────┼──────────────────┐
        ▼                 ▼                  ▼
 tools/git_tools.py tools/spotify_tools.py core/jarvis.py
  (branches, commits) (play/pause/skip)   (general chat,
                                            streamed via
                                            utils/groq.py)
                          │
                 ┌────────▼─────────┐
                 │  core/memory.py  │  rolling summary +
                 │  (SimpleMemory)  │  recent turn history
                 └───────────────────┘
                          │
              ┌───────────┴────────────┐
              ▼                        ▼
        app.py (PyQt6 HUD)     audio/test_piper.py (TTS)
```

- **`utils/groq.py`** is the single point of contact with the Groq API, exposing both a streaming chat call (`call_groq`) and a strict-schema structured call (`call_groq_structured`) used by the router and commit-message generator.
- **`core/router.py`** owns intent classification: a fast deterministic regex layer, then an LLM structured-output call validated against the `CommandPayload` schema, with a confidence threshold that demotes uncertain classifications to `general_chat`.
- **`core/memory.py`** persists conversation state per session as JSON in `data/`, using an LLM-generated rolling summary to compress older turns without losing named entities, preferences, or open threads.

---

## Repository Structure

```text
.
├── app.py                  # PyQt6 desktop UI (HUD, chat panel, streaming)
├── config.py                # Environment/config loader
├── main.py                  # Entry point: CLI + pipeline orchestration
├── requirements.txt
├── audio/
│   ├── test_ears.py         # Push-to-talk mic capture + speech recognition
│   └── test_piper.py        # Local neural TTS via Piper
├── core/
│   ├── jarvis.py             # General chat system prompt + Groq call
│   ├── memory.py              # Rolling summarized conversation memory
│   ├── router.py               # Intent classification + routing rules
│   └── schemas.py               # Pydantic CommandPayload schema
├── tools/
│   ├── git_tools.py          # Branch ops + AI commit message generation
│   └── spotify_tools.py        # Spotify playback via Spotipy + rapidfuzz
├── utils/
│   ├── groq.py                # Groq API client wrapper (chat + structured)
│   ├── helpers.py               # Shell command runner, ambiguity check
│   └── logger.py                 # Shared logging config
├── data/                      # Persisted memory + logs (gitignored)
└── voice_models/               # Piper .onnx voice model (gitignored)
```

---

## Requirements

- Python 3.12+
- A working microphone and speakers/headphones (for voice mode)
- A [Groq API key](https://console.groq.com/)
- A Piper voice model (`.onnx` + `.onnx.json`) placed in `voice_models/`
- *(Optional)* Spotify Developer app credentials, for playback control

Core dependencies (see `requirements.txt` for the full list):

`groq` · `pydantic` · `python-dotenv` · `SpeechRecognition` · `keyboard` · `numpy` · `sounddevice` · `piper-tts` · `PyQt6` · `spotipy` · `rapidfuzz`

---

## Installation

```powershell
# 1. Create and activate a virtual environment
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root:

```env
# Groq API
GROQ_API_KEY=your_groq_api_key
GROQ_FAST_MODEL=llama-3.1-8b-instant
GROQ_SMART_MODEL=llama-3.3-70b-versatile
GROQ_FAST_STRUCTURED_MODEL=openai/gpt-oss-20b
GROQ_SMART_STRUCTURED_MODEL=openai/gpt-oss-120b

# Voice
VOICE_MODEL_PATH=./voice_models/en_GB-alan-medium.onnx
SPEECH_SPEED=0.80
SPEECH_VOLUME=1.0

# Spotify (optional — leave unset to disable Spotify commands)
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8080/callback
```

> `GROQ_FAST_STRUCTURED_MODEL` / `GROQ_SMART_STRUCTURED_MODEL` must point to models that support Groq's `json_schema` strict-mode structured outputs (e.g. the `openai/gpt-oss-*` family).

---

## Usage

### Desktop UI (default)

```powershell
python main.py --window
```

Launches the frameless PyQt6 HUD. Type a command or question and press Enter/**SEND**. Responses stream live into the chat panel with a state-reactive glow (idle → processing → speaking).

### Terminal CLI

```powershell
python main.py --cli
```

- Type a prompt and press **Enter** to send it as text.
- Press **Enter** on an empty line to start push-to-talk voice input.
- Hold **M** while speaking, then release to finish recording.
- Type `quit`, `exit`, or `bye` to close the app.

**Examples:**

```text
create a git branch called feature/voice-ui
commit the staged changes
play reflections by the neighbourhood
pause music
what does this repo do?
```

---

## Supported Intents

| Intent | Trigger examples | Behavior |
|---|---|---|
| `git_commit` | "commit my changes" | Generates a Conventional Commit message from the staged diff, then asks for confirmation before committing and pushing |
| `git_create_branch` | "create a branch called feature/x" | Creates and switches to a new branch |
| `git_switch_branch` | "switch to main" | Switches to an existing branch |
| `git_delete_branch` | "delete the branch old-login" | Deletes the specified branch |
| `git_list_branches` | "list my branches" | Lists all local branches |
| `git_current_branch` | "what's my current branch?" | Reports the active branch |
| `spotify_play` | "play reflections by thenbhd" | Fuzzy-matched Spotify search and playback |
| `spotify_pause` | "pause" / "stop the music" | Pauses playback |
| `spotify_skip` | "next" / "skip" | Skips to the next track |
| `spotify_previous` | "back" / "previous track" | Returns to the previous track |
| `spotify_info` | "what song is this?" | Reports the currently playing track |
| `general_chat` | anything else — questions, opinions, coding help | Streamed conversational response from JARVIS's chat model |

---

## How Routing Works

1. **Deterministic pre-filter** — a small set of regex rules in `core/router.py` catches unambiguous commands (`pause`, `skip`, `current branch`, `list branches`) instantly, without an LLM call.
2. **LLM classification** — everything else is sent to a Groq structured-output call, guided by a system prompt with explicit disambiguation rules and few-shot examples (e.g. distinguishing "this song is good" from "play this song").
3. **Schema validation** — the response is validated against the `CommandPayload` Pydantic model (`intent`, `query`, `confidence`).
4. **Confidence gate** — if `confidence` falls below the configured threshold (`0.6`) and the classified intent isn't already `general_chat`, the router demotes the request to `general_chat` rather than risk executing the wrong action.

---

## Memory

`core/memory.py` implements `SimpleMemory`, which:

- Keeps the last N conversational turns (default 5) verbatim for context.
- When the buffer overflows, folds the oldest turns into a compact rolling summary using a dedicated LLM prompt tuned to preserve named entities, stated preferences/corrections, and open questions — while discarding filler and tool-execution noise.
- Persists both the recent history and the running summary to `data/memory_<session_id>.json`, so context survives across restarts.

---

## Spotify Integration

`tools/spotify_tools.py` authenticates via Spotipy's OAuth flow (cached client, refreshed automatically on `401` errors) and exposes:

- `play_music_smart(raw_query, corrected_query)` — searches Spotify with **both** the user's original phrasing and the router's LLM-corrected query, then scores every candidate with `rapidfuzz` token-set matching against both queries and plays the best match (rejecting low-confidence matches outright).
- `pause_music`, `skip_track`, `previous_track`, `get_current_playing_info`.

This dual-query approach exists specifically to handle romanized Urdu/Hindi and other transliterated titles, where an over-eager LLM correction can otherwise steer playback to the wrong track.

---

## Git Automation

`tools/git_tools.py` provides:

- `generate_git_commit_message` — stages all changes, pulls the diff, and asks the smart Groq model to produce a Conventional Commits–formatted message (with an optional body) grounded in the actual diff content.
- `execute_git_commit` / `cancel_git_commit` — commit-and-push or reset-and-unstage, gated behind an explicit user confirmation in both CLI and UI flows.
- `git_create_branch`, `git_switch_branch`, `git_delete_branch`, `git_list_branches`, `git_current_branch`.

> ⚠️ `git_commit` pushes immediately after committing. Review the proposed message carefully before confirming — this is a known area flagged for future safety improvements (see [Roadmap](#roadmap)).

---

## Roadmap

- [ ] Persist memory to SQLite once the data shape stabilizes (currently JSON)
- [ ] Deterministic slot-memory dict (`last_played_track`, `current_git_branch`, ...) updated directly from tool results rather than inferred by the LLM
- [ ] Swap the routing model to a stronger model and split classification from query normalization into two focused calls
- [ ] Fixed labeled regression test set to catch router drift over time
- [ ] Make `git_commit`'s auto-push after commit optional/configurable
- [ ] PC automation agent — screen/mouse control via computer vision + a multimodal LLM (PyAutoGUI-driven), planned for after the current fix pass

---

## Contributing

This is currently a personal project built incrementally, one fix at a time. Issues and pull requests are welcome — please keep changes scoped and explain the reasoning behind them in the PR description.

---

## License

Released under the [MIT License](LICENSE) © 2026 Muhammad Abdullah.