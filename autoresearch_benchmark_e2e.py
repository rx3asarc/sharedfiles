#!/usr/bin/env python3
"""
Benchmark true end-to-end latency: hotkey release → text in clipboard
This is the actual user-facing metric.
"""

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


def measure_e2e_latency(transcriber: WhisperTranscriber, duration_sec: float = 1.5) -> tuple:
    """Measure end-to-end latency: recording → transcription → clipboard.
    
    Simulates user releasing hotkey after speaking for `duration_sec`.
    
    Args:
        transcriber: WhisperTranscriber instance
        duration_sec: Duration of recorded speech
        
    Returns:
        Tuple of (e2e_latency_ms, memory_peak_mb, text)
    """
    # Create synthetic audio (simulates user recording)
    sample_rate = 16000
    num_samples = int(sample_rate * duration_sec)
    
    # Create a chirp-like pattern (frequency sweep) that resembles speech
    t = np.linspace(0, duration_sec, num_samples)
    freq_start = 200
    freq_end = 2000
    freq = np.linspace(freq_start, freq_end, num_samples)
    audio_data = (0.1 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
    audio_data += (0.02 * np.random.randn(num_samples)).astype(np.float32)
    audio_data = np.clip(audio_data, -1.0, 1.0)
    
    # Measure memory before
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 / 1024
    
    # TIME THE ENTIRE PIPELINE: transcription → clipboard
    # This simulates: user releases hotkey → Whisper processes → text in clipboard
    start_time = time.perf_counter()
    
    # 1. Transcribe (main bottleneck) - include local formatting
    text = transcriber.transcribe(audio_data, sample_rate, skip_formatting=False)
    
    # 2. Copy to clipboard (optimized for speed)
    try:
        copy_to_clipboard(text)
    except Exception:
        pass
    
    e2e_latency = (time.perf_counter() - start_time) * 1000  # ms
    
    # Measure memory after
    mem_after = process.memory_info().rss / 1024 / 1024
    memory_peak = max(mem_before, mem_after)
    
    return e2e_latency, memory_peak, text


def run_benchmark(num_runs: int = 3, duration_sec: float = 1.5) -> dict:
    """Run E2E latency benchmark.
    
    Args:
        num_runs: Number of runs to measure
        duration_sec: Duration of simulated speech
        
    Returns:
        Dict with metrics
    """
    # Load config
    config = Config.load()
    
    # Initialize transcriber (counts toward startup time, not E2E)
    try:
        transcriber = WhisperTranscriber(
            model_name=config.model_name,
            language=config.language,
            device=config.device_type,
            compute_type=config.compute_type
        )
    except Exception as e:
        print(f"ERROR: Failed to load model: {e}", file=sys.stderr)
        return None
    
    # Run benchmark multiple times and report median
    latencies = []
    memories = []
    texts = []
    
    for i in range(num_runs):
        try:
            latency, memory, text = measure_e2e_latency(transcriber, duration_sec)
            latencies.append(latency)
            memories.append(memory)
            texts.append(text)
            print(f"Run {i+1}/{num_runs}: {latency:.1f}ms, {memory:.1f}MB", file=sys.stderr)
        except Exception as e:
            print(f"ERROR in run {i+1}: {e}", file=sys.stderr)
            return None
    
    # Calculate medians
    median_latency = sorted(latencies)[len(latencies) // 2]
    median_memory = sorted(memories)[len(memories) // 2]
    
    return {
        'e2e_latency_ms': median_latency,
        'memory_mb': median_memory,
        'text_sample': texts[0][:50] if texts else ""
    }


if __name__ == "__main__":
    metrics = run_benchmark(num_runs=3, duration_sec=1.5)
    
    if metrics:
        # Output METRIC lines for autoresearch to parse
        print(f"METRIC e2e_latency={metrics['e2e_latency_ms']:.1f}")
        print(f"METRIC peak_memory={metrics['memory_mb']:.1f}")
        sys.exit(0)
    else:
        print("METRIC e2e_latency=0")
        print("METRIC peak_memory=0")
        sys.exit(0)
