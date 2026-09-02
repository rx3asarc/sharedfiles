#!/usr/bin/env python3
"""Measure UI rendering frame rate and latency"""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from voice_tui.config import Config
from voice_tui.ascii_app import VoiceToTextASCIIApp

class DummyController:
    """Dummy controller for testing"""
    def __init__(self):
        pass

# Create app
config = Config.load()
app = VoiceToTextASCIIApp(config, DummyController())

# Simulate rendering loop
print("Measuring rendering performance...")
print("(Simulating recording status with updates)")
print()

frame_times = []
for i in range(100):
    # Simulate metrics updates (like real recording)
    app.update_recording_metrics(duration=i*0.01, audio_level=0.5, peak_level=0.8)
    
    # Measure frame render time
    start = time.perf_counter()
    app._render_frame()
    frame_time = (time.perf_counter() - start) * 1000
    frame_times.append(frame_time)
    
    if i % 10 == 0:
        print(f"Frame {i}: {frame_time:.2f}ms")

print()
print(f"Average frame time: {sum(frame_times)/len(frame_times):.2f}ms")
print(f"Min frame time: {min(frame_times):.2f}ms")
print(f"Max frame time: {max(frame_times):.2f}ms")
print(f"Implied FPS: {1000 / (sum(frame_times)/len(frame_times)):.1f}")
print()
print("Target: 60 FPS (16.7ms per frame) for smooth rendering")
print("Current: 10 FPS (100ms per frame) as per SESSION_PROGRESS.md")
