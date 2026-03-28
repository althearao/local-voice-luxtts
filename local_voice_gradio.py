# Patch gradio_client boolean JSON schema bug (persists across reinstalls this way)
import gradio_client.utils as _gc_utils
_orig = _gc_utils._json_schema_to_python_type
def _patched(schema, defs):
    if isinstance(schema, bool):
        return "Any"
    return _orig(schema, defs)
_gc_utils._json_schema_to_python_type = _patched

import ollama
import soundfile as sf
import numpy as np
import tempfile
import os
import sys
import gradio as gr
from fastrtc import get_stt_model
from zipvoice.luxvoice import LuxTTS

# ── Config (students: change these two lines) ────────────────────────────────
OLLAMA_MODEL    = "class_murmur"        # your Ollama model name
REFERENCE_AUDIO = "./reference_voice.wav"  # optional at startup — can upload in UI
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = "You are a student doing student things."
OUTPUT_AUDIO  = "./tts_output.wav"      # fixed output file — overwritten each turn

# --- Startup check: Ollama ---
try:
    ollama.list()
except Exception:
    print("ERROR: Cannot connect to Ollama.")
    print("Start it first: run `ollama serve` in another terminal.")
    sys.exit(1)

# --- Load models ---
print("Loading STT (Moonshine)...")
stt_model = get_stt_model(model="moonshine/base")

print("Loading TTS (LuxTTS)...")
tts = LuxTTS('YatharthS/LuxTTS', device='cuda')  # auto-detects: cuda → mps → cpu

current_encoded = {"prompt": None}
if os.path.exists(REFERENCE_AUDIO):
    current_encoded["prompt"] = tts.encode_prompt(REFERENCE_AUDIO, duration=5, rms=0.01)
    print(f"Loaded default reference: {REFERENCE_AUDIO}")
else:
    print("No default reference_voice.wav found. Please upload one in the UI.")

print("Ready.")


# --- Pipeline functions ---

def transcribe(audio):
    sr, data = audio
    if data.ndim > 1:
        data = data.mean(axis=1)          # stereo → mono
    data = data.astype('float32')
    max_val = np.max(np.abs(data))
    if max_val == 0:
        return ""                          # silence guard
    data = data / max_val
    data_int16 = (data * 32767).astype(np.int16)
    return stt_model.stt((sr, data_int16))


def ask_llm(user_text, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for human, bot in history[-3:]:
        messages.append({"role": "user", "content": human})
        messages.append({"role": "assistant", "content": bot})
    messages.append({"role": "user", "content": user_text})
    response = ollama.chat(model=OLLAMA_MODEL, messages=messages)
    return response['message']['content']


def speak(text):
    if current_encoded["prompt"] is None:
        raise ValueError("No reference audio loaded. Please upload a reference voice file.")
    if len(text.split()) < 4:
        return None  # too short for TTS vocoder — skip silently
    wav = tts.generate_speech(
        text,
        encode_dict=current_encoded["prompt"],
        num_steps=4,
        t_shift=0.9,
        speed=1.0,
        return_smooth=False
    )
    wav = (np.clip(wav.squeeze(0).numpy(), -1.0, 1.0) * 32767).astype(np.int16)
    sf.write(OUTPUT_AUDIO, wav, 48000)
    return OUTPUT_AUDIO


def update_reference(audio_file):
    if audio_file is None:
        return "No file selected."
    current_encoded["prompt"] = tts.encode_prompt(audio_file, duration=5, rms=0.01)
    return f"Reference voice updated: {os.path.basename(audio_file)}"


def pipeline_voice(audio, history):
    if audio is None:
        return history, history, None
    try:
        user_text = transcribe(audio)
        if not user_text.strip():
            return history, history, None
        bot_text = ask_llm(user_text, history)
        audio_out = speak(bot_text)
        new_history = history + [(user_text, bot_text)]
        return new_history, new_history, audio_out
    except ollama.ResponseError as e:
        msg = f"LLM error: {e} — is '{OLLAMA_MODEL}' in `ollama list`?"
        return history + [("[mic]", msg)], history + [("[mic]", msg)], None
    except Exception as e:
        return history + [("[mic]", f"Error: {e}")], history + [("[mic]", f"Error: {e}")], None


def pipeline_text(text, history):
    if not text.strip():
        return history, history, None, ""
    try:
        bot_text = ask_llm(text, history)
        audio_out = speak(bot_text)
        new_history = history + [(text, bot_text)]
        return new_history, new_history, audio_out, ""
    except ollama.ResponseError as e:
        msg = f"LLM error: {e} — is '{OLLAMA_MODEL}' in `ollama list`?"
        return history + [(text, msg)], history + [(text, msg)], None, ""
    except Exception as e:
        return history + [(text, f"Error: {e}")], history + [(text, f"Error: {e}")], None, ""


# --- Gradio UI ---
_default_status = (
    f"Default {os.path.basename(REFERENCE_AUDIO)} loaded"
    if os.path.exists(REFERENCE_AUDIO)
    else "No reference audio — please upload one"
)

with gr.Blocks(title=f"Chatting with {OLLAMA_MODEL}") as demo:
    gr.Markdown(f"<center><h1>Chatting with {OLLAMA_MODEL}</h1></center>")

    with gr.Row():
        ref_upload = gr.Audio(
            sources=["upload"],
            type="filepath",
            label="Upload Reference Audio",
            scale=3
        )
        ref_status = gr.Textbox(
            label="Status",
            value=_default_status,
            interactive=False,
            scale=2
        )
    ref_upload.change(update_reference, inputs=[ref_upload], outputs=[ref_status])

    chatbot = gr.Chatbot(label="Conversation", height=400)
    history_state = gr.State([])

    with gr.Row():
        audio_in = gr.Audio(sources=["microphone"], type="numpy", label="Speak")
        audio_out = gr.Audio(label="Response", autoplay=True)

    with gr.Row():
        text_in = gr.Textbox(placeholder="Or type here...", label="Text input", scale=4)
        send_btn = gr.Button("Send", scale=1)

    audio_in.stop_recording(
        pipeline_voice,
        inputs=[audio_in, history_state],
        outputs=[chatbot, history_state, audio_out]
    )
    send_btn.click(
        pipeline_text,
        inputs=[text_in, history_state],
        outputs=[chatbot, history_state, audio_out, text_in]
    )
    text_in.submit(
        pipeline_text,
        inputs=[text_in, history_state],
        outputs=[chatbot, history_state, audio_out, text_in]
    )

demo.launch(server_name="127.0.0.1", server_port=7860)
