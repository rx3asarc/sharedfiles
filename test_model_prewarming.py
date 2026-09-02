#!/usr/bin/env python3
"""Test if pre-warming the model eliminates first-run penalty."""

import sys
import time
import numpy as np
from pathlib import Path
import threading

sys.path.insert(0, str(Path(__file__).parent))

from voice_tui.config import Config
from voice_tui.transcriber import WhisperTranscriber
from voice_tui.fast_clipboard import copy_to_clipboard

print("Testing Model Pre-Warming Impact")
print("="*70)

config = Config.load()

# Test 1: WITHOUT pre-warming (baseline)
print("\n1. WITHOUT pre-warming:")
transcriber1 = WhisperTranscriber(
    model_name=config.model_name,
    language=config.language,
    device=config.device_type,
    compute_type=config.compute_type
)

# Create test audio
sample_rate = 16000
duration = 1.5
num_samples = int(sample_rate * duration)
t = np.linspace(0, duration, num_samples)
freq = np.linspace(200, 2000, num_samples)
audio_data = (0.1 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
audio_data += (0.02 * np.random.randn(num_samples)).astype(np.float32)
audio_data = np.clip(audio_data, -1, 1)

# First run (cold)
start = time.perf_counter()
text1 = transcriber1.transcribe(audio_data, sample_rate, skip_formatting=True)
copy_to_clipboard(text1)
cold_time = (time.perf_counter() - start) * 1000

# Warm run
start = time.perf_counter()
text2 = transcriber1.transcribe(audio_data, sample_rate, skip_formatting=True)
copy_to_clipboard(text2)
warm_time = (time.perf_counter() - start) * 1000

print(f"  First run (cold):  {cold_time:.1f}ms")
print(f"  Second run (warm): {warm_time:.1f}ms")
print(f"  Penalty: {cold_time - warm_time:.1f}ms")

# Test 2: WITH pre-warming (async background)
print("\n2. WITH async pre-warming in background:")

class TranscriberWithPreWarming:
    def __init__(self, config):
        self.transcriber = WhisperTranscriber(
            model_name=config.model_name,
            language=config.language,
            device=config.device_type,
            compute_type=config.compute_type
        )
        # Pre-warm in background
        self._prewarm_thread = threading.Thread(target=self._prewarm, daemon=True)
        self._prewarm_thread.start()
    
    def _prewarm(self):
        """Pre-warm model with dummy transcription."""
        try:
            dummy_audio = np.zeros(16000, dtype=np.float32)
            self.transcriber.transcribe(dummy_audio, 16000, skip_formatting=True)
        except:
            pass
    
    def wait_for_warmup(self, timeout=5):
        """Wait for pre-warming to complete."""
        self._prewarm_thread.join(timeout=timeout)
    
    def transcribe(self, audio, sample_rate):
        """Transcribe (will be fast if pre-warming completed)."""
        return self.transcriber.transcribe(audio, sample_rate, skip_formatting=True)

transcriber2 = TranscriberWithPreWarming(config)

# First run (should be warmed up now)
start = time.perf_counter()
text3 = transcriber2.transcribe(audio_data, sample_rate)
copy_to_clipboard(text3)
prewarmed_time = (time.perf_counter() - start) * 1000

# Warm run
start = time.perf_counter()
text4 = transcriber2.transcribe(audio_data, sample_rate)
copy_to_clipboard(text4)
subsequent_time = (time.perf_counter() - start) * 1000

print(f"  First run (with prewarm): {prewarmed_time:.1f}ms")
print(f"  Second run:               {subsequent_time:.1f}ms")
print()

print("="*70)
if prewarmed_time < cold_time:
    saved = cold_time - prewarmed_time
    print(f"Pre-warming saved: {saved:.1f}ms ({(saved/cold_time)*100:.1f}%)")
else:
    print(f"Pre-warming had no benefit in this test")
