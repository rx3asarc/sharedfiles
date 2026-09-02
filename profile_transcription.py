#!/usr/bin/env python3
"""Profile transcription to identify bottlenecks"""

import sys
import cProfile
import pstats
import io
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from voice_tui.transcriber import WhisperTranscriber
import numpy as np

def profile_single_transcription():
    """Profile a single transcription call"""
    transcriber = WhisperTranscriber(model_name="base")
    
    # Create audio
    sample_rate = 16000
    duration = 1.5
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples)
    freq = np.linspace(200, 2000, num_samples)
    audio_data = (0.1 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
    audio_data += (0.02 * np.random.randn(num_samples)).astype(np.float32)
    audio_data = np.clip(audio_data, -1, 1)
    
    # Profile the transcription
    pr = cProfile.Profile()
    pr.enable()
    
    text = transcriber.transcribe(audio_data, sample_rate, skip_formatting=True)
    
    pr.disable()
    
    # Print stats
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # Top 20 functions
    print(s.getvalue())

if __name__ == "__main__":
    print("Profiling transcription (first 1.5s run)...")
    print()
    profile_single_transcription()
