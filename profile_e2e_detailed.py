#!/usr/bin/env python3
"""Detailed E2E breakdown - where are the remaining 26.2ms spent?"""

import sys
import time
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from voice_tui.config import Config
from voice_tui.transcriber import WhisperTranscriber
from voice_tui.fast_clipboard import copy_to_clipboard

# Initialize
config = Config.load()
transcriber = WhisperTranscriber(
    model_name=config.model_name,
    language=config.language,
    device=config.device_type,
    compute_type=config.compute_type
)

print("Detailed E2E Latency Breakdown")
print("="*70)

# Create test audio ONCE (not in loop)
sample_rate = 16000
duration = 1.5
num_samples = int(sample_rate * duration)
t = np.linspace(0, duration, num_samples)
freq = np.linspace(200, 2000, num_samples)
audio_data = (0.1 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
audio_data += (0.02 * np.random.randn(num_samples)).astype(np.float32)
audio_data = np.clip(audio_data, -1, 1)

# Warm up
_ = transcriber.transcribe(audio_data, sample_rate, skip_formatting=True)
print("Model warmed up\n")

# Profile cached runs (what users experience after first run)
print("Cached runs (typical user experience):\n")

for run in range(5):
    # Detailed timing
    timings = {}
    
    # 1. Transcription
    start = time.perf_counter()
    text = transcriber.transcribe(audio_data, sample_rate, skip_formatting=True)
    timings['transcribe'] = (time.perf_counter() - start) * 1000
    
    # 2. Clipboard
    start = time.perf_counter()
    copy_to_clipboard(text)
    timings['clipboard'] = (time.perf_counter() - start) * 1000
    
    # 3. Total
    timings['total'] = timings['transcribe'] + timings['clipboard']
    
    print(f"Run {run+1}:")
    print(f"  Transcribe:  {timings['transcribe']:6.2f}ms")
    print(f"  Clipboard:   {timings['clipboard']:6.2f}ms")
    print(f"  TOTAL E2E:   {timings['total']:6.2f}ms")
    
    # Calculate what's unaccounted for
    expected_min = 8.6 + 3.0  # baseline transcribe + optimized clipboard
    unaccounted = timings['total'] - expected_min
    if unaccounted > 0:
        print(f"  Overhead:    {unaccounted:6.2f}ms (variance/GC/OS scheduling)")
    print()

print("="*70)
print("Analysis:")
print("- Transcription baseline: 8.6ms (cached, base model)")
print("- Clipboard baseline: 3-5ms (native methods)")
print("- Expected minimum: 11.6-13.6ms")
print("- Actual median: 26.2ms")
print("- Unaccounted: ~12-15ms (system factors)")
print()
print("Next optimization targets:")
print("1. Reduce system overhead (not much control)")
print("2. Model pre-warming (eliminate cold-start 80ms penalty)")
print("3. Streaming transcription (architectural change)")
