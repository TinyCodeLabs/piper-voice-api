#!/usr/bin/env python3
import json
import os
import socket
import time
from pathlib import Path
import wave
from piper import PiperVoice, SynthesisConfig

VOICE_PATH = "/app/voices/"
DEFAULT_VOICE = "de_DE-thorsten-medium"

AUDIO_PATH = "/app/out/"
SOCKET_PATH = "/app/tts.sock"

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
    voice = data.get("voice", DEFAULT_VOICE)
    # speed = float(data.get("speed", DEFAULT_SPEED))
    filename = data.get("filename", f"output_{int(time.time())}.wav")

    if not text:
        raise ValueError("Missing 'text'")

    # if "<" in text and ">" in text:
    #     text = ssml_to_text(text)
   
    # Load the voice model
    voice = get_voice(VOICE_PATH + voice + ".onnx")

    # Configure synthesis parameters
    syn_config = SynthesisConfig(
        length_scale=1.0,
    )

    # Generate Audio
    generate_tts(text, filename, voice, syn_config)

    return {"status": "ok", "output": filename}
    
def safe_send(conn, payload: dict):
    try:
        conn.sendall(json.dumps(payload).encode("utf-8"))
    except (BrokenPipeError, OSError):
        pass

def main():
    # Ensure the output directory exists
    if not os.path.exists(AUDIO_PATH):
        os.makedirs(AUDIO_PATH)

    # Establish socket connection
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(SOCKET_PATH)
    sock.listen(5)

    print(f"Piper TTS socket listening on {SOCKET_PATH}")

    while True:
        conn, _ = sock.accept()
        try:
            while True:
                raw = conn.recv(1024 * 1024)               

                try:
                    data = json.loads(raw.decode("utf-8"))
                    result = handle_request(data)
                    safe_send(conn, result)
                except Exception as e:
                    safe_send(conn, {"status": "error", "error": str(e)})
        finally:
            conn.close()   

if __name__ == "__main__":
    main()
