"""
Audio Signal Processing module.
Analyzes voice activity, audio energy (RMS/dB), classroom speech vs silence ratio,
and detects interaction modes (Silence, Teacher Monologue, Active Discussion).
"""

import numpy as np

class AudioAnalyticsEngine:
    """Processes audio buffers to extract acoustic engagement indicators."""
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.silence_threshold_db = -45.0
        self.speech_threshold_db = -32.0
        self.recent_energy = []
        self.recent_speech_flags = []

    def compute_rms(self, audio_data):
        """Computes Root Mean Square (RMS) energy of audio signal."""
        if audio_data is None or len(audio_data) == 0:
            return 0.0
        if isinstance(audio_data, bytes):
            # Convert raw 16-bit PCM bytes to numpy float array
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        elif isinstance(audio_data, np.ndarray):
            audio_array = audio_data.astype(np.float32)
            if audio_array.max() > 1.0 or audio_array.min() < -1.0:
                audio_array = audio_array / 32768.0
        else:
            audio_array = np.array(audio_data, dtype=np.float32)

        if len(audio_array) == 0:
            return 0.0

        rms = float(np.sqrt(np.mean(audio_array ** 2)))
        return rms

    def compute_db(self, rms):
        """Converts RMS value to decibels relative to full scale (dBFS)."""
        if rms <= 1e-7:
            return -90.0
        return float(20.0 * np.log10(rms))

    def compute_zero_crossing_rate(self, audio_array):
        """Calculates zero-crossing rate to characterize speech vs background noise."""
        if len(audio_array) < 2:
            return 0.0
        signs = np.sign(audio_array)
        signs[signs == 0] = 1
        zcr = float(np.sum(np.abs(np.diff(signs))) / (2.0 * len(audio_array)))
        return zcr

    def analyze_audio_chunk(self, audio_data):
        """
        Processes audio slice (live microphone or media stream).
        Returns:
            dict containing rms, db, is_speech, interaction_mode, audio_score
        """
        rms = self.compute_rms(audio_data)
        db = self.compute_db(rms)

        is_speech = db > self.speech_threshold_db
        self.recent_energy.append(db)
        self.recent_speech_flags.append(1 if is_speech else 0)

        # Keep rolling window of last 30 frames (~15-30 seconds)
        if len(self.recent_energy) > 30:
            self.recent_energy.pop(0)
            self.recent_speech_flags.pop(0)

        speech_ratio = np.mean(self.recent_speech_flags) if self.recent_speech_flags else 0.0
        energy_variance = float(np.var(self.recent_energy)) if len(self.recent_energy) > 2 else 0.0

        # Classify classroom acoustic interaction mode
        if speech_ratio < 0.10:
            interaction_mode = "Independent Study / Silence"
            audio_score = 65.0
        elif speech_ratio > 0.85 and energy_variance < 15.0:
            interaction_mode = "Teacher Monologue"
            audio_score = 60.0
        elif 0.25 <= speech_ratio <= 0.75 and energy_variance >= 15.0:
            interaction_mode = "Active Discussion / Student Q&A"
            audio_score = 92.0
        else:
            interaction_mode = "Guided Instruction"
            audio_score = 78.0

        return {
            "rms": round(rms, 4),
            "db": round(db, 1),
            "is_speech": bool(is_speech),
            "speech_ratio": round(speech_ratio, 2),
            "interaction_mode": interaction_mode,
            "audio_score": round(audio_score, 1)
        }
