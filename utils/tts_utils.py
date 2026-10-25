"""
Text-to-Speech (TTS) Engine module.
Generates audio alerts, spoken teaching suggestions, and audio artifacts
in the storage layer as specified in the technical architecture.
"""

import os
import wave
import struct
import math
from pathlib import Path
from config import Config, AUDIO_DIR

class TextToSpeechEngine:
    """Manages audio feedback generation for teaching suggestions."""
    def __init__(self):
        self.output_dir = AUDIO_DIR

    def generate_tone_alert(self, filename="alert.wav", duration=0.6, frequency=440.0):
        """Generates a pleasant chime WAV file for attention alerts."""
        file_path = self.output_dir / filename
        sample_rate = 22050
        num_samples = int(duration * sample_rate)

        with wave.open(str(file_path), 'w') as wav_file:
            wav_file.setnchannels(1)        # mono
            wav_file.setsampwidth(2)        # 16-bit
            wav_file.setframerate(sample_rate)

            for i in range(num_samples):
                t = float(i) / sample_rate
                # Dual-tone chord with gentle exponential decay envelope
                decay = math.exp(-3.0 * t / duration)
                val1 = math.sin(2.0 * math.pi * frequency * t)
                val2 = math.sin(2.0 * math.pi * (frequency * 1.25) * t)
                sample = int(32767.0 * 0.4 * (val1 + val2) * decay)
                wav_file.writeframes(struct.pack('<h', sample))

        return str(file_path)

    def synthesize_suggestion_notice(self, suggestion_text, suggestion_id=1):
        """
        Creates an audio record placeholder and returns structured metadata
        for client-side browser speech synthesis or local audio playback.
        """
        tone_path = self.generate_tone_alert(f"suggestion_{suggestion_id}.wav", duration=0.5, frequency=523.25)
        return {
            "audio_file": str(Path(tone_path).name),
            "spoken_text": suggestion_text,
            "engine": "WebSpeechAPI + SyntheticChime"
        }
