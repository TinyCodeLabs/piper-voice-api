#!/usr/bin/env python3
import os
import wave
from piper import PiperVoice, SynthesisConfig

VOICE_PATH = "/home/tim/projects/piper-voice-api/piper-tts/voices/de_DE-thorsten-medium.onnx"

AUDIO_PATH = "./out/"

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

def main():
    # Ensure the output directory exists
    if not os.path.exists(AUDIO_PATH):
        os.makedirs(AUDIO_PATH)

    # Load the voice model
    voice = get_voice(VOICE_PATH)

    # Configure synthesis parameters
    syn_config = SynthesisConfig(
        length_scale=1.0,
    )

    # Generate Audio
    generate_tts("Hallo, ich bin eine Teststimme.", "test.wav", voice, syn_config)
    

if __name__ == "__main__":
    main()
