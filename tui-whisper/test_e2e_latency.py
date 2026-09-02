#!/usr/bin/env python3
"""End-to-end latency test: hotkey release → text in clipboard"""

import sys
import time
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from voice_tui.config import Config
from voice_tui.transcriber import WhisperTranscriber
from voice_tui.recorder import AudioRecorder
import pyperclip

def simulate_e2e_latency():
    """Simulate complete workflow: record → transcribe → clipboard"""
    
    # Initialize (happens once at startup)
    config = Config.load()
    transcriber = WhisperTranscriber(
        model_name=config.model_name,
        language=config.language,
        device=config.device_type,
        compute_type=config.compute_type
    )
    
    # Simulate 1.5 seconds of user speech (realistic short utterance)
    sample_rate = 16000
    duration = 1.5
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples)
    freq = np.linspace(200, 2000, num_samples)
    
    # Create audio data (user speaking)
    audio_data = (0.1 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
    audio_data += (0.02 * np.random.randn(num_samples)).astype(np.float32)
    audio_data = np.clip(audio_data, -1, 1)
    
    # Measure end-to-end latency
    start = time.perf_counter()
    
    # 1. Transcribe
    text = transcriber.transcribe(audio_data, sample_rate, skip_formatting=True)
    
    # 2. Copy to clipboard
    try:
        pyperclip.copy(text)
    except:
        pass
    
    e2e_latency = (time.perf_counter() - start) * 1000
    
    return e2e_latency, text

print("End-to-End Latency Test")
print("Simulating: User speaks (1.5s) -> Release hotkey -> Text in clipboard")
print()

# Run multiple times
latencies = []
for i in range(5):
    latency, text = simulate_e2e_latency()
    latencies.append(latency)
    print(f"Run {i+1}: {latency:.1f}ms ('{text[:40]}...')")

print()
print(f"Median: {sorted(latencies)[len(latencies)//2]:.1f}ms")
print(f"Best: {min(latencies):.1f}ms")
print(f"Worst: {max(latencies):.1f}ms")
