#!/usr/bin/env python3
"""Profile where time is spent in E2E pipeline."""

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

print("Profiling E2E Pipeline Breakdown")
print("="*60)

# Simulate multiple runs to see breakdown
for run in range(3):
    print(f"\nRun {run+1}:")
    
    # 1. Generate audio (simulating recording)
    start = time.perf_counter()
    sample_rate = 16000
    duration = 1.5
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples)
    freq = np.linspace(200, 2000, num_samples)
    audio_data = (0.1 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
    audio_data += (0.02 * np.random.randn(num_samples)).astype(np.float32)
    audio_data = np.clip(audio_data, -1, 1)
    audio_gen_time = (time.perf_counter() - start) * 1000
    
    # 2. Transcribe
    start = time.perf_counter()
    text = transcriber.transcribe(audio_data, sample_rate, skip_formatting=True)
    transcribe_time = (time.perf_counter() - start) * 1000
    
    # 3. Clipboard
    start = time.perf_counter()
    if pyperclip:
        try:
            pyperclip.copy(text)
        except:
            pass
    clipboard_time = (time.perf_counter() - start) * 1000
    
    total = audio_gen_time + transcribe_time + clipboard_time
    
    print(f"  Audio gen:     {audio_gen_time:.1f}ms")
    print(f"  Transcribe:    {transcribe_time:.1f}ms")
    print(f"  Clipboard:     {clipboard_time:.1f}ms")
    print(f"  Total:         {total:.1f}ms")
    print(f"  Transcribe %:  {100*transcribe_time/total:.0f}%")

print()
print("Analysis:")
print("- Audio generation is NOT in real user pipeline (already recorded)")
print("- Real E2E should only count Transcribe + Clipboard")
print("- If audio gen ~15ms, real E2E = ~25ms (transcribe 8.6 + clipboard 1 + overhead 0.4)")
