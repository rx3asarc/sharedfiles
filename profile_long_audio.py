#!/usr/bin/env python3
"""Test latency scaling with longer audio durations (the real issue!)"""

import sys
import time
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from voice_tui.config import Config
from voice_tui.transcriber import WhisperTranscriber

# Initialize
config = Config.load()
transcriber = WhisperTranscriber(
    model_name=config.model_name,
    language=config.language,
    device=config.device_type,
    compute_type=config.compute_type
)

print("Latency Scaling Test - Short vs Long Audio")
print("="*70)
print("Simulating user recording for different durations\n")

durations = [1.5, 5, 10, 30, 60]

for duration in durations:
    print(f"Recording Duration: {duration}s")
    
    # Create synthetic audio of specified duration
    sample_rate = 16000
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples)
    freq = np.linspace(200, 2000, num_samples)
    audio_data = (0.1 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
    audio_data += (0.02 * np.random.randn(num_samples)).astype(np.float32)
    audio_data = np.clip(audio_data, -1, 1)
    
    # Warm-up (first run includes model caching effects)
    _ = transcriber.transcribe(audio_data, sample_rate, skip_formatting=True)
    
    # Measure 2 runs (skip first)
    latencies = []
    for run in range(2):
        start = time.perf_counter()
        text = transcriber.transcribe(audio_data, sample_rate, skip_formatting=True)
        latency = (time.perf_counter() - start) * 1000
        latencies.append(latency)
        if run == 0:
            print(f"  Run 1 (warm):  {latency:6.1f}ms - text length: {len(text)} chars")
        else:
            print(f"  Run 2 (cache): {latency:6.1f}ms - text length: {len(text)} chars")
    
    # Estimate scaling
    if duration > 1.5:
        scale_factor = duration / 1.5
        baseline_cached = 8.6  # ms for 1.5s audio (our current best)
        predicted = baseline_cached * scale_factor
        actual = latencies[1]
        ratio = actual / predicted
        print(f"  Predicted at {scale_factor:.1f}x scale: {predicted:.1f}ms")
        print(f"  Ratio (actual/predicted): {ratio:.2f}x\n")
    else:
        print()

print("="*70)
print("KEY INSIGHT:")
print("- If 1 min (60s) audio takes 1 min to transcribe, something is VERY wrong")
print("- Should scale roughly linearly: 60/1.5 = 40x longer audio = ~40x longer time")
print("- So 1 min audio should take ~344ms (8.6 * 40), NOT 60000ms")
print("- If user says it feels like 4-5 minutes, latency must be 240,000+ ms = 4+ minutes!")
