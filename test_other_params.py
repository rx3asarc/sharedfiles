#!/usr/bin/env python3
"""Test other Whisper parameters for optimization."""

import sys
import time
import numpy as np
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

print("Testing various parameters")
print("="*60)

# Test patience
print("\nTesting patience parameter:")
for patience in [1, 0.5, 0]:
    latencies = []
    for run in range(2):
        try:
            start = time.perf_counter()
            segments, info = model.transcribe(
                audio_data, language="en", vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=100),
                best_of=1, beam_size=7, temperature=0.0,
                patience=patience
            )
            latency = (time.perf_counter() - start) * 1000
            latencies.append(latency)
        except Exception as e:
            print(f"  patience={patience}: ERROR - {e}")
            break
    if latencies:
        print(f"  patience={patience}: {statistics.median(latencies):.1f}ms (runs: {', '.join(f'{l:.1f}' for l in latencies)})")

# Test length_penalty
print("\nTesting length_penalty parameter:")
for lp in [0.8, 1.0, 1.2]:
    latencies = []
    for run in range(2):
        start = time.perf_counter()
        segments, info = model.transcribe(
            audio_data, language="en", vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=100),
            best_of=1, beam_size=7, temperature=0.0,
            length_penalty=lp
        )
        latency = (time.perf_counter() - start) * 1000
        latencies.append(latency)
    median = sorted(latencies)[0]
    print(f"  length_penalty={lp}: {median:.1f}ms (runs: {', '.join(f'{l:.1f}' for l in latencies)})")

# Test suppress_blank
print("\nTesting suppress_blank parameter:")
for sb in [True, False]:
    latencies = []
    for run in range(2):
        start = time.perf_counter()
        segments, info = model.transcribe(
            audio_data, language="en", vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=100),
            best_of=1, beam_size=7, temperature=0.0,
            suppress_blank=sb
        )
        latency = (time.perf_counter() - start) * 1000
        latencies.append(latency)
    median = sorted(latencies)[0]
    print(f"  suppress_blank={sb}: {median:.1f}ms (runs: {', '.join(f'{l:.1f}' for l in latencies)})")

import statistics
