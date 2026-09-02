#!/usr/bin/env python3
"""Test different VAD silence thresholds to find optimal latency."""

import sys
import time
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from voice_tui.config import Config
from voice_tui.transcriber import WhisperTranscriber
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

# Test different VAD thresholds
thresholds = [50, 75, 100, 150, 200]
print("Testing VAD silence duration thresholds")
print("="*50)

config = Config.load()
model = WhisperModel(config.model_name, device="cpu", compute_type="int8")

# Warmup
_ = model.transcribe(audio_data, language="en", vad_filter=True, 
                     vad_parameters=dict(min_silence_duration_ms=100))

results = []
for threshold in thresholds:
    latencies = []
    for run in range(3):
        start = time.perf_counter()
        segments, info = model.transcribe(
            audio_data,
            language="en",
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=threshold),
            best_of=1,
            temperature=0.0
        )
        latency = (time.perf_counter() - start) * 1000
        latencies.append(latency)
    
    median = sorted(latencies)[1]
    results.append((threshold, median, latencies))
    print(f"VAD {threshold}ms: {median:.1f}ms (runs: {', '.join(f'{l:.1f}' for l in latencies)})")

print()
print("Summary:")
best_threshold, best_latency, _ = min(results, key=lambda x: x[1])
print(f"Best: {best_threshold}ms ({best_latency:.1f}ms latency)")
