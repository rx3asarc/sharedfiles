#!/usr/bin/env python3
"""Test different beam_size values."""

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
                     best_of=1, temperature=0.0)

# Test different beam sizes
beam_sizes = [3, 5, 7, 10]
print("Testing beam_size parameter")
print("="*50)

for beam_size in beam_sizes:
    latencies = []
    for run in range(3):
        start = time.perf_counter()
        segments, info = model.transcribe(
            audio_data,
            language="en",
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=100),
            best_of=1,
            temperature=0.0,
            beam_size=beam_size
        )
        latency = (time.perf_counter() - start) * 1000
        latencies.append(latency)
    
    median = sorted(latencies)[1]
    print(f"beam_size={beam_size}: {median:.1f}ms (runs: {', '.join(f'{l:.1f}' for l in latencies)})")

print()
print("Note: beam_size is independent of best_of")
print("beam_size controls search breadth, best_of controls candidate count")
