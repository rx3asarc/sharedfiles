#!/usr/bin/env python3
"""Measure UI rendering computation time (without terminal output)"""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from voice_tui.config import Config
from voice_tui.ascii_app import VoiceToTextASCIIApp

class DummyController:
    pass

# Create app
config = Config.load()
app = VoiceToTextASCIIApp(config, DummyController())

print("Measuring rendering computation time...")
print("(Without terminal I/O)")
print()

# Monkey patch to skip terminal output
original_render = app.buffer.render_to_terminal
app.buffer.render_to_terminal = lambda: None

frame_times = []
for i in range(100):
    # Simulate metrics updates
    app.update_recording_metrics(duration=i*0.01, audio_level=0.5, peak_level=0.8)
    
    # Measure frame computation time (excluding terminal I/O)
    start = time.perf_counter()
    app._render_frame()
    frame_time = (time.perf_counter() - start) * 1000
    frame_times.append(frame_time)
    
    if i % 20 == 0:
        print(f"Frame {i}: {frame_time:.2f}ms")

print()
print(f"Average frame computation: {sum(frame_times)/len(frame_times):.2f}ms")
print(f"Min: {min(frame_times):.2f}ms")
print(f"Max: {max(frame_times):.2f}ms")
print(f"Std dev: {(sum((x - sum(frame_times)/len(frame_times))**2 for x in frame_times) / len(frame_times))**0.5:.2f}ms")
print()
print("With 10 FPS target (100ms per frame):")
print("  Computation: {:.1f}%".format(sum(frame_times)/len(frame_times) / 100 * 100))
