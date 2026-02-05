#!/usr/bin/env python3

import wave
from piper import PiperVoice, SynthesisConfig

VOICE_PATH = "piper-tts/voices/de_DE-thorsten-medium.onnx"


# ---------------- Main socket loop ----------------
def main():
    voice = PiperVoice.load(VOICE_PATH)

    syn_config = SynthesisConfig(
        length_scale=1.0,
    )

    with wave.open("out.wav", "wb") as wav:
        for chunk in voice.synthesize("Hello streaming world", syn_config=syn_config):
            wav.setnchannels(chunk.sample_channels)
            wav.setsampwidth(chunk.sample_width)
            wav.setframerate(chunk.sample_rate)

            wav.writeframes(chunk.audio_int16_bytes)

if __name__ == "__main__":
    main()
