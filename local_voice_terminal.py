import ollama
import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import os
import sys
from zipvoice.luxvoice import LuxTTS

# ── Config (students: change these two lines) ────────────────────────────────
OLLAMA_MODEL   = "john"        # your Ollama model name
REFERENCE_AUDIO = "./reference_voice.m4a"  # 5–10s voice clip (.wav .mp3 .m4a …)
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = "You are a student doing student things."

# --- Startup checks ---
if not os.path.exists(REFERENCE_AUDIO):
    print(f"ERROR: Reference audio not found: {REFERENCE_AUDIO}")
    print("Place a 5–10 second voice recording in the project folder and update REFERENCE_AUDIO.")
    sys.exit(1)

try:
    ollama.list()
except Exception:
    print("ERROR: Cannot connect to Ollama.")
    print("Start it first: run `ollama serve` in another terminal.")
    sys.exit(1)

print("Loading TTS (LuxTTS)...")
tts = LuxTTS('YatharthS/LuxTTS', device='cuda')
encoded_prompt = tts.encode_prompt(REFERENCE_AUDIO, duration=5, rms=0.01)
print("Ready.\n")

history = []


def ask_llm(user_text):
    history.append({"role": "user", "content": user_text})
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history[-6:]
    )
    reply = response['message']['content']
    history.append({"role": "assistant", "content": reply})
    return reply


def speak(text):
    wav = tts.generate_speech(
        text,
        encode_dict=encoded_prompt,
        num_steps=4,
        t_shift=0.9,
        speed=1.0,
        return_smooth=False
    )
    wav = (np.clip(wav.squeeze(0).numpy(), -1.0, 1.0) * 32767).astype(np.int16)
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(tmp.name, wav, 48000)
    data, sr = sf.read(tmp.name)
    os.unlink(tmp.name)
    sd.play(data, sr)
    sd.wait()


print("Type your message. Ctrl+C to quit.\n")
while True:
    try:
        user_text = input("You: ").strip()
        if not user_text:
            continue
        try:
            reply = ask_llm(user_text)
            print(f"{OLLAMA_MODEL}: {reply}\n")
            speak(reply)
        except ollama.ResponseError as e:
            print(f"[LLM error] {e} — is '{OLLAMA_MODEL}' in `ollama list`?\n")
        except Exception as e:
            print(f"[Error] {e}\n")
    except KeyboardInterrupt:
        print("\nGoodbye.")
        break
