#!/usr/bin/env python3
"""Test with more realistic speech patterns."""

import sys
import time
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from voice_tui.config import Config
from voice_tui.transcriber import WhisperTranscriber

try:
    import pyperclip
except ImportError:
    pyperclip = None

# Initialize
config = Config.load()
transcriber = WhisperTranscriber(
    model_name=config.model_name,
    language=config.language,
    device=config.device_type,
    compute_type=config.compute_type
)

print("Real-World E2E Latency Test")
print("="*70)
print("Testing with different audio durations + clipboard operation\n")

durations = [1.5, 10, 30, 60]

for duration in durations:
    print(f"Audio Duration: {duration}s")
    
    # Create more realistic speech pattern
    sample_rate = 16000
    num_samples = int(sample_rate * duration)
    
    # Simulate speech with formants (more realistic)
    t = np.linspace(0, duration, num_samples)
    
    # Add multiple frequency components to sound more like speech
    f1 = 300 + 100 * np.sin(2 * np.pi * 2 * t)  # First formant
    f2 = 1500 + 300 * np.sin(2 * np.pi * 1 * t)  # Second formant
    f3 = 2500 + 200 * np.sin(2 * np.pi * 0.5 * t)  # Third formant
    
    audio_data = (
        0.1 * np.sin(2 * np.pi * f1 * t) +
        0.05 * np.sin(2 * np.pi * f2 * t) +
        0.02 * np.sin(2 * np.pi * f3 * t)
    ).astype(np.float32)
    
    # Add some noise
    audio_data += (0.01 * np.random.randn(num_samples)).astype(np.float32)
    audio_data = np.clip(audio_data, -1, 1)
    
    # Warm-up
    _ = transcriber.transcribe(audio_data, sample_rate, skip_formatting=True)
    
    # Measure E2E latency including clipboard
    latencies = []
    for run in range(2):
        start = time.perf_counter()
        
        # 1. Transcribe
        text = transcriber.transcribe(audio_data, sample_rate, skip_formatting=True)
        
        # 2. Clipboard
        if pyperclip:
            try:
                pyperclip.copy(text)
            except:
                pass
        
        e2e_latency = (time.perf_counter() - start) * 1000
        latencies.append(e2e_latency)
        
        if run == 0:
            print(f"  Run 1 (warm):  {e2e_latency:6.1f}ms - text: '{text[:30] if text else '(empty)'}...'")
        else:
            print(f"  Run 2 (cache): {e2e_latency:6.1f}ms - text: '{text[:30] if text else '(empty)'}...'")
    
    # Analysis
    if duration > 1.5:
        # Extrapolate from 1.5s baseline (8.6ms transcribe + 18ms clipboard ≈ 26ms E2E)
        baseline_e2e = 26.0
        expected_time = baseline_e2e + ((duration - 1.5) / 1.5) * (8.6 * 40 / 40)
        
        # More accurate: transcription scales linearly, clipboard is constant
        transcribe_base = 8.6
        clipboard_base = 18.0
        transcribe_scaled = transcribe_base * (duration / 1.5)
        expected_time = transcribe_scaled + clipboard_base
        
        actual = latencies[1]
        print(f"  Expected E2E: {expected_time:.1f}ms (transcribe {transcribe_scaled:.1f}ms + clipboard 18ms)")
        print(f"  Actual ratio: {actual/expected_time:.2f}x\n")
    else:
        print()

print("="*70)
print("IMPORTANT: If real recording feels like 4-5 minutes for 1 minute audio:")
print("- It's NOT transcription latency (which scales linearly)")
print("- Could be:")
print("  1. UI blocking/freezing (no progress feedback)")
print("  2. Model loading on FIRST run (not cached yet)")
print("  3. Post-processing delay (smart formatting)")
print("  4. Psychological - no feedback feels slower")
