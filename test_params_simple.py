#!/usr/bin/env python3
"""Quick test of alternative parameters."""

import sys
import time
import numpy as np
import statistics
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from voice_tui.config import Config
from faster_whisper import WhisperModel

# Create test audio
sample_rate = 16000
duration = 1.5
num_samples = int(sample_rate * duration)
t = np.linspace(0, duration, num_samples)
freq = np.linspace(200, 2000, num_samples)
audio_data = (0.1 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
audio_data += (0.02 * np.random.randn(num_samples)).astype(np.float32)
audio_data = np.clip(audio_data, -1, 1)

config = Config.load()
model = WhisperModel(config.model_name, device="cpu", compute_type="int8")

# Warmup
_ = model.transcribe(audio_data, language="en", vad_filter=True, 
                     vad_parameters=dict(min_silence_duration_ms=100),
                     best_of=1, beam_size=7, temperature=0.0)

print("Testing alternative parameters")
print("="*60)

# Test patience
print("\nPatience values:")
for patience in [1, 0.5]:
    latencies = []
    for run in range(2):
        start = time.perf_counter()
        segments, info = model.transcribe(
            audio_data, language="en", vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=100),
            best_of=1, beam_size=7, temperature=0.0,
            patience=patience
        )
        latency = (time.perf_counter() - start) * 1000
        latencies.append(latency)
    median = statistics.median(latencies)
    print(f"  patience={patience}: {median:.1f}ms")

# Test no_repeat_ngram_size
print("\nNo-repeat n-gram size:")
for n in [0, 2]:
    latencies = []
    for run in range(2):
        start = time.perf_counter()
        segments, info = model.transcribe(
            audio_data, language="en", vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=100),
            best_of=1, beam_size=7, temperature=0.0,
            no_repeat_ngram_size=n
        )
        latency = (time.perf_counter() - start) * 1000
        latencies.append(latency)
    median = statistics.median(latencies)
    print(f"  no_repeat_ngram_size={n}: {median:.1f}ms")
