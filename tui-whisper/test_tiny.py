#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from voice_tui.config import Config
from voice_tui.transcriber import WhisperTranscriber
from voice_tui.recorder import AudioRecorder
import time
import numpy as np

config = Config.load()
config.model_name = "tiny"  # Use tiny for quick test

transcriber = WhisperTranscriber(
    model_name="tiny",
    language="en"
)

sample_rate = 16000
duration = 2.0
num_samples = int(sample_rate * duration)
t = np.linspace(0, duration, num_samples)
freq = np.linspace(200, 2000, num_samples)
audio_data = (0.1 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
audio_data += (0.02 * np.random.randn(num_samples)).astype(np.float32)
audio_data = np.clip(audio_data, -1.0, 1.0)

# Warm run
start = time.perf_counter()
text = transcriber.transcribe(audio_data, sample_rate)
latency = (time.perf_counter() - start) * 1000

print(f"Tiny model first run: {latency:.1f}ms")

for i in range(2):
    start = time.perf_counter()
    text = transcriber.transcribe(audio_data, sample_rate)
    latency = (time.perf_counter() - start) * 1000
    print(f"Run {i+2}: {latency:.1f}ms")
