#!/usr/bin/env python3
import json
import os
import socket
import time
from pathlib import Path
import traceback
import wave
from piper import PiperVoice, SynthesisConfig

VOICE_PATH = "/app/voices/"
DEFAULT_VOICE = "de_DE-thorsten-medium"

AUDIO_PATH = "/app/out/"
SOCKET_PATH = "/app/run/tts.sock"

VOICE_CACHE: dict[str, PiperVoice] = {}

def get_voice(model_path: str) -> PiperVoice:
    if model_path not in VOICE_CACHE:
        VOICE_CACHE[model_path] = PiperVoice.load(model_path)
    return VOICE_CACHE[model_path]

def generate_tts(text: str, filename: str, voice: PiperVoice, syn_config: SynthesisConfig) -> bytes:
    with wave.open(AUDIO_PATH + filename, "wb") as wav:
        for chunk in voice.synthesize(text, syn_config=syn_config):
            wav.setnchannels(chunk.sample_channels)
            wav.setsampwidth(chunk.sample_width)
            wav.setframerate(chunk.sample_rate)

            wav.writeframes(chunk.audio_int16_bytes)

def handle_request(data: dict) -> dict:
    text = data.get("text", "")
    voicename = data.get("voice", DEFAULT_VOICE)
    # speed = float(data.get("speed", DEFAULT_SPEED))
    filename = data.get("filename", f"output_{int(time.time())}.wav")

    if not text:
        raise ValueError("Missing 'text'")

    # if "<" in text and ">" in text:
    #     text = ssml_to_text(text)
   
    # Load the voice model
    voice = get_voice(VOICE_PATH + voicename + ".onnx")

    # Configure synthesis parameters
    syn_config = SynthesisConfig(
        length_scale=1.0,
    )
    print(voicename, filename, " - ", text)
    # Generate Audio
    generate_tts(text, filename, voice, syn_config)

    return {"status": "ok", "output": filename}
    
def safe_send(conn, payload: dict):
    try:
        conn.sendall(json.dumps(payload).encode("utf-8"))
    except (BrokenPipeError, OSError):
        pass

def main():
    while True:
        try:
            run_server()
        except Exception as e:
            print("🔥 Server crashed:", e)
            traceback.print_exc()
            print("Restarting socket in 2 seconds...")
            time.sleep(2)


def run_server():
    # Ensure output directory exists
    os.makedirs(AUDIO_PATH, exist_ok=True)
    os.makedirs("/app/run", exist_ok=True)

    # Remove stale socket file
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(SOCKET_PATH)
    os.chmod(SOCKET_PATH, 0o660)
    sock.listen(5)

    print(f"Piper TTS socket listening on {SOCKET_PATH}")

    while True:
        conn, _ = sock.accept()
        print("Client connected")

        with conn:
            try:
                raw = conn.recv(1024 * 1024)

                if not raw:
                    # Client closed connection immediately
                    continue

                data = json.loads(raw.decode("utf-8"))
                result = handle_request(data)
                safe_send(conn, result)

            except Exception as e:
                safe_send(conn, {"status": "error", "error": str(e)})

        print("Client disconnected")

if __name__ == "__main__":
    main()
