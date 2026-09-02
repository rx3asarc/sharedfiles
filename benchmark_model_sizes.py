#!/usr/bin/env python3
"""Compare latency and memory across different Whisper model sizes."""

import sys
import time
import numpy as np
import psutil
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from voice_tui.transcriber import WhisperTranscriber

def benchmark_model(model_name: str, num_runs: int = 3) -> dict:
    """Benchmark a specific model size.
    
    Args:
        model_name: Model name (tiny, base, small, medium, large-v3)
        num_runs: Number of runs to average
        
    Returns:
        Dict with latency and memory stats
    """
    print(f"\n{'='*50}")
    print(f"Testing model: {model_name}")
    print('='*50)
    
    try:
        # Initialize model
        print(f"Loading {model_name} model...", end=" ", flush=True)
        init_start = time.perf_counter()
        transcriber = WhisperTranscriber(model_name=model_name)
        init_time = (time.perf_counter() - init_start) * 1000
        print(f"Done ({init_time:.0f}ms)")
        
        # Create test audio
        sample_rate = 16000
        duration = 1.5
        num_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, num_samples)
        freq = np.linspace(200, 2000, num_samples)
        audio_data = (0.1 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
        audio_data += (0.02 * np.random.randn(num_samples)).astype(np.float32)
        audio_data = np.clip(audio_data, -1, 1)
        
        # Get memory
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024
        
        # Warm-up run (not counted)
        print("Warming up...", end=" ", flush=True)
        _ = transcriber.transcribe(audio_data, sample_rate)
        print("Done")
        
        # Measure runs
        latencies = []
        for i in range(num_runs):
            start = time.perf_counter()
            text = transcriber.transcribe(audio_data, sample_rate)
            latency = (time.perf_counter() - start) * 1000
            latencies.append(latency)
            print(f"  Run {i+1}: {latency:.1f}ms")
        
        mem_after = process.memory_info().rss / 1024 / 1024
        
        return {
            'model': model_name,
            'init_time_ms': init_time,
            'median_latency_ms': sorted(latencies)[len(latencies)//2],
            'min_latency_ms': min(latencies),
            'max_latency_ms': max(latencies),
            'peak_memory_mb': mem_after,
            'memory_delta_mb': mem_after - mem_before,
            'text_sample': text[:50]
        }
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None

# Benchmark models
models_to_test = ['tiny', 'base', 'small']
results = []

print("Model Size Comparison Benchmark")
print(f"Testing {len(models_to_test)} models with {1.5}s speech audio")

for model in models_to_test:
    result = benchmark_model(model)
    if result:
        results.append(result)

# Summary table
print(f"\n{'='*80}")
print("SUMMARY")
print('='*80)
print(f"{'Model':<10} {'Init':<8} {'Median':<8} {'Min':<8} {'Max':<8} {'Memory':<10} {'Delta':<8}")
print('-'*80)

for r in results:
    print(f"{r['model']:<10} {r['init_time_ms']:>6.0f}ms {r['median_latency_ms']:>6.1f}ms {r['min_latency_ms']:>6.1f}ms {r['max_latency_ms']:>6.1f}ms {r['peak_memory_mb']:>8.0f}MB {r['memory_delta_mb']:>6.0f}MB")

print()
print("Comparison to baseline (base model):")
for r in results:
    if r['model'] != 'base':
        base_latency = [x['median_latency_ms'] for x in results if x['model'] == 'base'][0]
        improvement = ((base_latency - r['median_latency_ms']) / base_latency) * 100
        print(f"  {r['model']:>6} vs base: {improvement:+.1f}% latency")

print()
print("Recommendations:")
print("- tiny: fastest, lowest memory, acceptable for casual use")
print("- base: good balance of speed and accuracy (current)")
print("- small: slowest, highest memory, best accuracy")
