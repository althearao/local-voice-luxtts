# Local Voice AI Chatbot

A fully local voice chatbot pipeline running on your local machine — no cloud, no API keys. Everything runs on your own hardware.

**Recommended system requirements:**
- Apple Silicon Mac (M1/M2/M3/M4) with 16GB RAM — ~15 seconds per response
- Windows PC with an NVIDIA GPU (4GB VRAM or more) and 16GB RAM
- CPU-only machines will work but will be slower

**Minimum:**
- 8GB RAM
- 10GB free disk space (for models and dependencies)

```
Microphone → STT (Moonshine) → LLM (Ollama) → TTS (LuxTTS) → Speaker
```

Two scripts included:
| Script | Description |
|--------|-------------|
| `local_voice_terminal.py` | Type text → LLM responds → plays audio |
| `local_voice_gradio.py` | Browser UI: speak or type → STT → LLM → TTS |

---

This repo is developed for my course, How to be Human in the Age of AI, at SJSU. Prior to deploying this lab, students should have gone through the following lab exercises:

- **Finetuning with Unsloth** with a bespoke dataset — the lab produces a `.gguf` file.
- **Interacting with the finetuned model locally** — the lab teaches students to register the `.gguf` file with Ollama and interact with it using the command line tool.

## Prerequisites

### 1. Ollama
Open **Terminal** (Mac) or **PowerShell** (Windows) and type:

```bash
ollama run //type your model name such as john, class_murmur
```

Hit enter. Keep Ollama running in the background while using the scripts.

### 2. Homebrew (Mac only)
If you don't have Homebrew already, open **Terminal** and run:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 3. uv (package manager)

**macOS** — open **Terminal** and type:
```bash
brew install uv
# or:
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows** — open **PowerShell** and type:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 4. Create a project folder

Create a new folder on your computer where all the project files will live. A few rules:
- No spaces in the folder name (use `local-voice` not `local voice`)
- Put it somewhere you can find easily — Desktop or Documents works fine
- Remember where it is — you'll need to navigate to it in Terminal / PowerShell

### 5. Reference voice file
A 5–10 second audio clip of a voice you want the AI to clone.
- Any format works: `.wav`, `.mp3`, `.m4a`
- Clear speech, no background music
- Place it in the project folder and note the filename

---

## Installation

Before running any commands, navigate Terminal / PowerShell into your project folder. Open Terminal / Powershell and type `cd` followed by a space, then drag your project folder into the Terminal / PowerShell window — the path will fill in automatically. Press Enter.

```bash
cd   # type this, add a space, then drag your folder in
```

### macOS (Apple Silicon — M1/M2/M3)

Open **Terminal** and type the following commands one at a time:

```bash
# 1. Clone this repo
git clone https://github.com/althearao/local-voice-luxtts
cd local-voice-luxtts

# 2. Create isolated Python 3.12 environment
uv venv --python 3.12 .venv
source .venv/bin/activate

# 3. Install LuxTTS dependencies (pinned for compatibility)
uv pip install -r LuxTTS/requirements.txt "numba<0.62" "llvmlite<0.46"

# 4. Install LuxTTS as a package
uv pip install -e LuxTTS/

# 5. Downgrade NumPy for torch compatibility
uv pip install "numpy<2"

# 6. Install remaining dependencies
uv pip install "fastrtc[stt]==0.0.19" ollama gradio soundfile sounddevice
```

### Windows

Open **Command Prompt** or **PowerShell** and type the following commands one at a time:

```bat
# 1. Clone this repo
git clone https://github.com/althearao/local-voice-luxtts
cd local-voice-luxtts

# 2. Create isolated Python 3.12 environment
uv venv --python 3.12 .venv

# 3. Activate the environment
# Command Prompt:
.venv\Scripts\activate
# PowerShell:
# .venv\Scripts\Activate.ps1

# 4. Install LuxTTS dependencies
uv pip install -r LuxTTS/requirements.txt "numba<0.62" "llvmlite<0.46"

# 5. Install LuxTTS as a package
uv pip install -e LuxTTS/

# 6. Downgrade NumPy for torch compatibility
uv pip install "numpy<2"

# 7. Install remaining dependencies
uv pip install "fastrtc[stt]==0.0.19" ollama gradio soundfile sounddevice
```

> **NVIDIA GPU (optional):** The scripts will automatically detect and use your GPU. No extra steps needed — torch installs CUDA support by default on Windows.

> **No GPU:** CPU inference works fine, but TTS generation will be slower than GPU-accelerated hardware.

---

## Configuration

Open local_voice_terminal.py or local_voice_gradio.py using VS Code or any code editor of your choice (VS Code is recommended for my students) Change **lines 11–12** (terminal) or **lines 14–15** (gradio):

```python
OLLAMA_MODEL    = "john"             # ← your model name 
REFERENCE_AUDIO = "./reference_voice.wav" # ← your voice file (any audio format)
```

That's the only change required.

---

## Running

Make sure your virtual environment is active (`source .venv/bin/activate` on Mac, `.venv\Scripts\activate` on Windows) before running.

### Terminal version (no browser needed)
Open **Terminal** (Mac) or **PowerShell** (Windows) and type:
```bash
python local_voice_terminal.py
```
Type a message and press Enter. The AI responds in text and speaks the reply.
`Ctrl+C` to quit.

### Gradio version (browser UI with microphone)
Open **Terminal** (Mac) or **PowerShell** (Windows) and type:
```bash
python local_voice_gradio.py
```
Open **http://127.0.0.1:7860** in your browser.

- **Upload Reference Audio** — click the upload box and select your voice file (or place `reference_voice.wav` in the project folder to skip this step)
- **Speak** — click the microphone, speak, release — the AI responds in your cloned voice
- **Or type** — use the text box and hit Send

---

## First-run notes

- **LuxTTS model download:** On first run, LuxTTS downloads ~1 GB of model weights from HuggingFace. This only happens once and is cached for future runs. The progress bar (`Fetching 11 files`) is normal.
- **Warnings are normal:** Messages about `k2`, `FNV hashing`, and deprecated Whisper flags appear on every run — they don't affect functionality.

---

## Troubleshooting

**`ERROR: Cannot connect to Ollama`**
Ollama isn't running. Start it:
```bash
ollama serve    # Mac / Linux
# On Windows: Ollama runs as a background service after install — check the system tray
```

**`LLM error: model not found`**
Your `OLLAMA_MODEL` name doesn't match what's installed. Check with:
```bash
ollama list
```
Model names are case-sensitive. Use the exact name shown.

**`No reference audio loaded`** (Gradio)
Upload a voice file using the Upload Reference Audio box at the top of the UI, or place a file named `reference_voice.wav` in the project folder before starting.

**`ModuleNotFoundError: No module named 'zipvoice'`**
LuxTTS wasn't installed as a package. Run:
```bash
uv pip install -e LuxTTS/
```

**`_ARRAY_API not found` or NumPy error**
NumPy 2.x is incompatible with torch 2.4.x. Run:
```bash
uv pip install "numpy<2"
```

**Windows: `.venv\Scripts\Activate.ps1` blocked by PowerShell**
Run this once to allow local scripts:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Audio doesn't play (terminal version)**
Make sure your system's default audio output is set. On Mac, check System Settings → Sound. On Windows, check the taskbar speaker icon.

---

## Project structure

```
local-voice-luxtts/
├── local_voice_terminal.py   # Terminal chatbot
├── local_voice_gradio.py     # Gradio browser UI
├── LuxTTS/                   # Patched LuxTTS (MPS + gradio fixes included)
├── requirements-locked.txt   # Exact locked versions (for reference)
└── README.md
```

> **Note on LuxTTS:** This repo includes a patched copy of [LuxTTS](https://github.com/ysharma3501/LuxTTS) with fixes for Apple Silicon MPS compatibility and a gradio_client schema bug. You do not need to clone the original LuxTTS repo separately.

---

## Hardware tested

| Platform | Status |
|----------|--------|
| Apple Silicon (M1/M2/M3) | ✅ Tested |
| Windows (NVIDIA GPU) | ✅ Expected to work |
| Windows (CPU only) | ✅ Expected to work (slower TTS) |
| Intel Mac | ⚠️ Requires Python 3.12; torch limited to 2.4.1 |

---

## How voice cloning works

The pipeline uses three pieces of technology stacked together.

**LuxTTS** is an open-source project by Yatharth Sharma that wraps a research model called **ZipVoice** — https://arxiv.org/abs/2506.13053 a 2025 paper from Xiaomi Corporation, authored by Han Zhu, Wei Kang, Zengwei Yao, and others including Daniel Povey (one of the most cited speech researchers in the world, also creator of the Kaldi toolkit). The audio output stage uses **Vocos**, a vocoder by Hubert Siuzdak published at ICLR 2024 https://arxiv.org/abs/2306.00814.

### How it works in plain language

Think of it as four stages: **listening**, **learning to speak**, **sculpting sound**, and **converting to audio**.

**Stage 1 — Listening to the reference voice.**
You hand the system a short clip (3–10 seconds). Instead of memorizing the recording, the system extracts a *vocal fingerprint* — a list of numbers describing the timbre, resonance, breath texture, and rhythm unique to that voice.

**Stage 2 — Learning language as shape.**
ZipVoice was trained on 100,000 hours of multilingual speech. From that, it learned that language has physical shape — syllables have duration, pitch curves, energy patterns. It uses a neural network called a Zipformer to turn your text into a blueprint: *this word should be long, this one short, this one rising.*

**Stage 3 — Sculpting the sound (flow matching).**
This is the generative step. The model starts with pure noise — like static — and gradually sculpts it into speech over 4 steps. The vocal fingerprint from Stage 1 steers the sculpting so the result sounds like *that specific voice* saying your new text. (Older systems needed 100+ steps; this runs at 150x realtime.)

**Stage 4 — Converting math to audio (the vocoder).**
The sculpting produces a spectrogram — a heatmap of frequencies over time, like sheet music made visible. Vocos converts that heatmap into actual audio using Fourier transforms, the same math used in EQ and audio analysis.

The model never "records" a voice and plays it back. It learns an abstract description of a voice's character, then uses that description to *generate entirely new audio* that was never spoken. It's more like learning an accent than copying a recording — which is exactly why it raises the questions it does.

### Where the training data came from

ZipVoice was trained on the **Emilia dataset** — 101,000+ hours of speech assembled by a separate research team. The audio was scraped from the internet: video platforms, podcasts, talk shows, interviews, debates, sports commentary, and audiobooks. The expanded version used YouTube videos with CC-BY 3.0 licenses, meaning creators had explicitly allowed reuse with attribution. Six languages are covered: English, Mandarin Chinese, German, French, Japanese, and Korean.

Raw internet audio is not optimized for training, so the researchers built a six-stage automated cleaning pipeline: standardize the format, strip background music, isolate individual speakers, chop into 3–30 second chunks, transcribe with Whisper, then filter out anything with poor audio quality or low language confidence. Only about **29% of the raw data survived** filtering.


---

## Credits

- [LuxTTS](https://github.com/ysharma3501/LuxTTS) by Yatharth Sharma — voice cloning TTS wrapper
- [ZipVoice](https://github.com/k2-fsa/ZipVoice) by Han Zhu, Wei Kang, et al. (Xiaomi Corp.) — underlying TTS model ([paper](https://arxiv.org/abs/2506.13053))
- [Vocos](https://github.com/gemelo-ai/vocos) by Hubert Siuzdak — neural vocoder ([paper](https://arxiv.org/abs/2306.00814))
- [Moonshine](https://github.com/usefulsensors/moonshine) via fastrtc — speech-to-text
- [Ollama](https://ollama.com) — local LLM inference
- Sahil Mhatre, teaching and research assistantance
- Concept and direction by Althea Rao; implementation assisted by [Claude](https://claude.ai) (Anthropic)

---

## License

**Code** — [Apache License 2.0](LICENSE). You are free to use, modify, and distribute the scripts and source code with attribution. This repo includes a patched copy of LuxTTS, which is also Apache 2.0.

**Documentation and course materials** (this README, written explanations, lab instructions) — [Creative Commons Attribution 4.0 International (CC-BY 4.0)](https://creativecommons.org/licenses/by/4.0/). You are free to share and adapt with attribution.
