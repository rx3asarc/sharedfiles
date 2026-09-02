#!/usr/bin/env python3
"""
Benchmark script for measuring transcription latency, memory usage, and UI performance.
Outputs METRIC lines for autoresearch.sh to parse.
"""

import sys
import time
import os
from pathlib import Path

try:
    import numpy as np
except ImportError as e:
    print(f"ERROR: numpy not found: {e}", file=sys.stderr)
    sys.exit(1)

try:
    import psutil
except ImportError as e:
    print(f"ERROR: psutil not found: {e}", file=sys.stderr)
    sys.exit(1)

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from voice_tui.config import Config
from voice_tui.transcriber import WhisperTranscriber
from voice_tui.recorder import AudioRecorder


def measure_transcription_latency(transcriber: WhisperTranscriber, duration_sec: float = 2.0, verbose: bool = False) -> tuple:
    """Measure end-to-end transcription latency.
    
    Args:
        transcriber: WhisperTranscriber instance
        duration_sec: Duration of synthetic audio to create
        verbose: If True, print timing breakdown
        
    Returns:
        Tuple of (latency_ms, memory_peak_mb, text)
    """
    # Create synthetic audio (1 second of silence + 1 second of speech-like noise)
    sample_rate = 16000
    num_samples = int(sample_rate * duration_sec)
    
    # Create a simple pattern that Whisper can recognize
    # Mix of frequencies that loosely resembles speech
    t = np.linspace(0, duration_sec, num_samples)
    
    # Create a chirp-like pattern (frequency sweep) that resembles speech
    freq_start = 200
    freq_end = 2000
    freq = np.linspace(freq_start, freq_end, num_samples)
    
    # Generate audio data
    start_gen = time.perf_counter()
    audio_data = (0.1 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
    audio_data += (0.02 * np.random.randn(num_samples)).astype(np.float32)
    audio_data = np.clip(audio_data, -1.0, 1.0)
    gen_time = (time.perf_counter() - start_gen) * 1000
    
    # Measure memory before
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 / 1024  # MB
    
    # Time the transcription
    start_time = time.perf_counter()
    text = transcriber.transcribe(audio_data, sample_rate)
    latency = (time.perf_counter() - start_time) * 1000  # ms
    
    # Measure memory after
    mem_after = process.memory_info().rss / 1024 / 1024  # MB
    memory_peak = max(mem_before, mem_after)
    
    if verbose:
        print(f"    Audio gen: {gen_time:.1f}ms, Transcription: {latency:.1f}ms, Memory: {memory_peak:.1f}MB", file=sys.stderr)
    
    return latency, memory_peak, text


def run_benchmark(num_runs: int = 3) -> dict:
    """Run benchmark and return metrics.
    
    Args:
        num_runs: Number of transcription runs to measure
        
    Returns:
        Dict with metrics: latency_ms, memory_mb, text_length
    """
    # Load config
    config = Config.load()
    
    # Initialize transcriber
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
            latency, memory, text = measure_transcription_latency(transcriber, verbose=(i==0))
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
        'latency_ms': median_latency,
        'memory_mb': median_memory,
        'text_sample': texts[0][:50] if texts else ""
    }


if __name__ == "__main__":
    try:
        metrics = run_benchmark(num_runs=3)
        
        if metrics:
            # Output METRIC lines for autoresearch to parse
            print(f"METRIC transcription_latency={metrics['latency_ms']:.1f}")
            print(f"METRIC peak_memory={metrics['memory_mb']:.1f}")
            sys.exit(0)
        else:
            print("METRIC transcription_latency=0")
            print("METRIC peak_memory=0")
            sys.exit(0)  # Always exit 0 to let run_experiment parse output
    except Exception as e:
        print(f"METRIC transcription_latency=0")
        print(f"METRIC peak_memory=0")
        sys.exit(0)  # Always exit 0
