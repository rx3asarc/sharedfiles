#!/usr/bin/env python3
"""Measure memory usage at different stages"""

import sys
import gc
import psutil
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

process = psutil.Process(os.getpid())

print("Memory at startup:")
mem_start = process.memory_info().rss / 1024 / 1024
print(f"  RSS: {mem_start:.1f} MB")

print("\nLoading transcriber...")
from voice_tui.transcriber import WhisperTranscriber
mem_after_imports = process.memory_info().rss / 1024 / 1024
print(f"  RSS: {mem_after_imports:.1f} MB (+{mem_after_imports - mem_start:.1f} MB)")

print("\nInitializing transcriber...")
transcriber = WhisperTranscriber(model_name="base")
mem_after_init = process.memory_info().rss / 1024 / 1024
print(f"  RSS: {mem_after_init:.1f} MB (+{mem_after_init - mem_after_imports:.1f} MB)")

print("\nCreating audio...")
import numpy as np
sample_rate = 16000
duration = 1.5
num_samples = int(sample_rate * duration)
t = np.linspace(0, duration, num_samples)
freq = np.linspace(200, 2000, num_samples)
audio_data = (0.1 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
audio_data += (0.02 * np.random.randn(num_samples)).astype(np.float32)
audio_data = np.clip(audio_data, -1, 1)
mem_after_audio = process.memory_info().rss / 1024 / 1024
print(f"  RSS: {mem_after_audio:.1f} MB (+{mem_after_audio - mem_after_init:.1f} MB)")

print("\nTranscribing...")
text = transcriber.transcribe(audio_data, sample_rate, skip_formatting=True)
mem_after_transcribe = process.memory_info().rss / 1024 / 1024
print(f"  RSS: {mem_after_transcribe:.1f} MB (+{mem_after_transcribe - mem_after_audio:.1f} MB)")

print(f"\nPeak memory: {mem_after_transcribe:.1f} MB")
print(f"Model size: ~140 MB (base model)")
print(f"Other overhead: {mem_after_transcribe - 140:.1f} MB")
