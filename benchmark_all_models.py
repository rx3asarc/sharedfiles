#!/usr/bin/env python3
"""Test E2E latency across all model sizes while keeping code unchanged."""

import sys
import subprocess
import statistics
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from voice_tui.config import Config
from voice_tui.transcriber import WhisperTranscriber
from voice_tui.fast_clipboard import copy_to_clipboard
import time
import numpy as np

# Models to test
MODELS = ['tiny', 'base', 'small']

print("Multi-Model E2E Latency Comparison")
print("="*70)
print("All optimizations (VAD, best_of, temperature, beam_size) apply equally\n")

results = {}

for model_name in MODELS:
    print(f"Testing model: {model_name}")
    print("-" * 70)
    
    try:
        # Load model
        transcriber = WhisperTranscriber(model_name=model_name, language='en')
        
        # Create test audio
        sample_rate = 16000
        duration = 1.5
        num_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, num_samples)
        freq = np.linspace(200, 2000, num_samples)
        audio_data = (0.1 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
        audio_data += (0.02 * np.random.randn(num_samples)).astype(np.float32)
        audio_data = np.clip(audio_data, -1, 1)
        
        # Warm up
        _ = transcriber.transcribe(audio_data, sample_rate, skip_formatting=True)
        
        # Measure E2E latency (transcribe + clipboard)
        latencies = []
        for run in range(5):
            start = time.perf_counter()
            text = transcriber.transcribe(audio_data, sample_rate, skip_formatting=True)
            copy_to_clipboard(text)
            latency = (time.perf_counter() - start) * 1000
            latencies.append(latency)
        
        median = statistics.median(latencies)
        results[model_name] = median
        
        print(f"  E2E Latency (5 runs):")
        print(f"    Median: {median:.1f}ms")
        print(f"    Min:    {min(latencies):.1f}ms")
        print(f"    Max:    {max(latencies):.1f}ms")
        print()
        
    except Exception as e:
        print(f"  ERROR: {e}\n")
        results[model_name] = None

# Summary
print("="*70)
print("SUMMARY - Model Comparison")
print("="*70)
print(f"{'Model':<10} {'E2E (ms)':<12} {'Relative':<12} {'Trade-off'}")
print("-" * 70)

if results['base']:
    base_latency = results['base']
    for model, latency in sorted(results.items(), key=lambda x: x[1] if x[1] else float('inf')):
        if latency:
            relative = latency / base_latency
            if model == 'tiny':
                tradeoff = "Faster, lower accuracy"
            elif model == 'base':
                tradeoff = "Balanced (recommended)"
            elif model == 'small':
                tradeoff = "Slower, higher accuracy"
            else:
                tradeoff = ""
            
            print(f"{model:<10} {latency:>10.1f}ms   {relative:>6.2f}x base   {tradeoff}")

print()
print("KEY: All models use SAME optimizations (VAD, parameters)")
print("     Switch models by changing 'model_name' in config.yaml or --model flag")
print("     Progress (git commits, optimizations) carries forward to all models")
