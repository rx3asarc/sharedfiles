#!/usr/bin/env python3
"""Benchmark 30-second audio E2E latency with parameter sweeps."""

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

def create_30s_audio():
    """Create 30 seconds of audio that passes VAD and yields transcription."""
    sample_rate = 16000
    duration_sec = 30.0
    num_samples = int(sample_rate * duration_sec)

    # Simulate speech with multiple formants and amplitude envelope
    t = np.linspace(0, duration_sec, num_samples)

    # Base carrier: mix of three formants (typical speech)
    f1 = 500 + 100 * np.sin(2 * np.pi * 0.2 * t)   # First formant (vowel quality)
    f2 = 1500 + 200 * np.sin(2 * np.pi * 0.25 * t)  # Second formant
    f3 = 2500 + 150 * np.sin(2 * np.pi * 0.3 * t)  # Third formant

    # Combine formants with different strengths
    audio = (
        0.08 * np.sin(2 * np.pi * f1 * t) +
        0.04 * np.sin(2 * np.pi * f2 * t) +
        0.02 * np.sin(2 * np.pi * f3 * t)
    ).astype(np.float32)

    # Add slight amplitude modulation to simulate syllabic rhythm
    envelope = 0.8 + 0.2 * np.sin(2 * np.pi * 4 * t)  # 4 Hz modulation (syllable rate)
    audio *= envelope

    # Add background noise (low level)
    audio += (0.005 * np.random.randn(num_samples)).astype(np.float32)

    # Introduce brief pauses (100-300ms of near-silence) every 5 seconds to test VAD
    pause_every = 5 * sample_rate  # 5 seconds
    pause_samples = int(0.2 * sample_rate)  # 200ms pause
    for start in range(0, num_samples, int(pause_every * 1.5)):
        pause_start = start + int(0.5 * sample_rate)  # pause halfway through segment
        if pause_start + pause_samples < num_samples:
            audio[pause_start:pause_start+pause_samples] *= 0.05  # deep fade to near silence

    audio = np.clip(audio, -1.0, 1.0)

    return audio, sample_rate

def measure_e2e_latency(transcriber, audio, sample_rate):
    """Measure end-to-end latency for given audio."""
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
    print("=== 30-Second Audio E2E Latency Benchmark ===", file=sys.stderr)
    print("Creating 30s speech-like audio...", file=sys.stderr)

    audio, sample_rate = create_30s_audio()
    print(f"Audio: {len(audio)/sample_rate:.1f}s, {len(audio)} samples, rms={np.sqrt(np.mean(audio**2)):.3f}", file=sys.stderr)

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

    # Warm up with short audio
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

if __name__ == "__main__":
    main()
