#!/usr/bin/env python3
"""Measure E2E latency including local formatting."""

import sys
import time
import numpy as np
import psutil
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from voice_tui.config import Config
from voice_tui.transcriber import WhisperTranscriber
from voice_tui.fast_clipboard import copy_to_clipboard

# Create test audio (same as benchmark)
sample_rate = 16000
duration_sec = 1.5
num_samples = int(sample_rate * duration_sec)
t = np.linspace(0, duration_sec, num_samples)
freq = np.linspace(200, 2000, num_samples)
audio_data = (0.1 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
audio_data += (0.02 * np.random.randn(num_samples)).astype(np.float32)
audio_data = np.clip(audio_data, -1, 1)

# Load transcriber with local formatting (skip_formatting=False)
config = Config.load()
transcriber = WhisperTranscriber(
    model_name=config.model_name,
    language=config.language,
    device=config.device_type,
    compute_type=config.compute_type
)

# Warm up
_ = transcriber.transcribe(audio_data, sample_rate, skip_formatting=False)

# Measure with formatting
print("Measuring E2E latency (transcription + local formatting + clipboard)...", file=sys.stderr)
latencies = []
memories = []

for run in range(5):
    start = time.perf_counter()
    text = transcriber.transcribe(audio_data, sample_rate, skip_formatting=False)
    copy_to_clipboard(text)
    elapsed = (time.perf_counter() - start) * 1000

    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / 1024 / 1024

    latencies.append(elapsed)
    memories.append(mem)
    print(f"Run {run+1}: {elapsed:.2f}ms, mem={mem:.1f}MB, text=\"{text[:40]}...\"", file=sys.stderr)

median_latency = sorted(latencies)[len(latencies)//2]
median_mem = sorted(memories)[len(memories)//2]

print(f"\nMEAN: {np.mean(latencies):.2f}ms")
print(f"MEDIAN: {median_latency:.2f}ms")
print(f"MIN/MAX: {min(latencies):.2f}/{max(latencies):.2f}ms")
print(f"\nMETRIC e2e_latency={median_latency:.1f}")
print(f"METRIC peak_memory={median_mem:.1f}")
