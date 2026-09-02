#!/usr/bin/env python3
"""Benchmark E2E latency with real 30-second audio file."""

import sys
import time
import numpy as np
import psutil
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from voice_tui.config import Config
from voice_tui.transcriber import WhisperTranscriber
from voice_tui.fast_clipboard import copy_to_clipboard
import soundfile as sf

AUDIO_FILE = "Recording.wav"

def load_audio():
    """Load the 30-second audio file."""
    if not os.path.exists(AUDIO_FILE):
        print(f"ERROR: Audio file '{AUDIO_FILE}' not found. Please record it first.", file=sys.stderr)
        return None, None

    audio, sr = sf.read(AUDIO_FILE)
    # Ensure float32 mono
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)  # convert to mono
    if audio.dtype != np.float32:
        audio = audio.astype(np.float32)
    return audio, sr

def measure_e2e_latency(transcriber, audio, sample_rate):
    """Measure end-to-end latency: transcription + clipboard."""
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 / 1024

    start_time = time.perf_counter()
    text = transcriber.transcribe(audio, sample_rate, skip_formatting=False)
    copy_to_clipboard(text)
    e2e_latency = (time.perf_counter() - start_time) * 1000

    mem_after = process.memory_info().rss / 1024 / 1024
    memory_peak = max(mem_before, mem_after)

    return e2e_latency, memory_peak, text

def run_benchmark(transcriber, audio, sample_rate, num_runs=3):
    """Run benchmark multiple times."""
    latencies = []
    memories = []
    texts = []

    for i in range(num_runs):
        try:
            latency, memory, text = measure_e2e_latency(transcriber, audio, sample_rate)
            latencies.append(latency)
            memories.append(memory)
            texts.append(text)
            print(f"  Run {i+1}: {latency:.1f}ms, {memory:.1f}MB, text_len={len(text)}", file=sys.stderr)
        except Exception as e:
            print(f"  ERROR in run {i+1}: {e}", file=sys.stderr)
            return None

    median_latency = sorted(latencies)[len(latencies) // 2]
    median_memory = sorted(memories)[len(memories) // 2]

    return {
        'e2e_latency_ms': median_latency,
        'memory_mb': median_memory,
        'text_sample': texts[0][:50] if texts else ""
    }

def main():
    print("=== 30-Second Real Audio Benchmark ===", file=sys.stderr)

    # Load audio
    print(f"Loading audio from {AUDIO_FILE}...", file=sys.stderr)
    audio, sample_rate = load_audio()
    if audio is None:
        return 1
    print(f"Audio: {len(audio)/sample_rate:.1f}s, sample_rate={sample_rate}, rms={np.sqrt(np.mean(audio**2)):.3f}", file=sys.stderr)

    # Load config
    config = Config.load()
    print(f"Model: {config.model_name}, Device: {config.device_type}, Compute: {config.compute_type}", file=sys.stderr)

    # Initialize transcriber
    print("Loading transcriber...", file=sys.stderr)
    transcriber = WhisperTranscriber(
        model_name=config.model_name,
        language=config.language,
        device=config.device_type,
        compute_type=config.compute_type
    )

    # Warm up with short audio (to avoid first-call overhead in measurement)
    warm_audio = audio[:int(sample_rate * 0.5)]
    print("Warming up...", file=sys.stderr)
    _ = transcriber.transcribe(warm_audio, sample_rate, skip_formatting=True)

    # Run benchmark
    print("\nRunning benchmark (3 runs)...\n", file=sys.stderr)
    metrics = run_benchmark(transcriber, audio, sample_rate, num_runs=3)

    if metrics:
        print(f"\nMETRIC e2e_latency={metrics['e2e_latency_ms']:.1f}")
        print(f"METRIC peak_memory={metrics['memory_mb']:.1f}")
    else:
        print("METRIC e2e_latency=0")
        print("METRIC peak_memory=0")

    return 0

if __name__ == "__main__":
    sys.exit(main())
