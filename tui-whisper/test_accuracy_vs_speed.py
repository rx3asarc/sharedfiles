#!/usr/bin/env python3
"""Test beam_size impact on transcription quality and speed for 30s real audio."""

import sys
import time
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from voice_tui.config import Config
from voice_tui.transcriber import WhisperTranscriber
import soundfile as sf

AUDIO_FILE = "test_30s.wav"

def load_audio():
    audio, sr = sf.read(AUDIO_FILE)
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)
    if audio.dtype != np.float32:
        audio = audio.astype(np.float32)
    return audio, sr

def test_beam_size(beam_size, audio, sr, config):
    """Test specific beam_size and return time + text."""
    # Load model fresh (expensive but necessary)
    from faster_whisper import WhisperModel
    model = WhisperModel(
        config.model_name,
        device=config.device_type,
        compute_type=config.compute_type
    )

    # Warm up with short audio
    warm = audio[:int(sr * 0.5)]
    _ = model.transcribe(warm, language=config.language, vad_filter=True, vad_parameters=dict(min_silence_duration_ms=100), best_of=1, beam_size=beam_size, temperature=0.0)

    # Measure transcription (no formatting to isolate model quality)
    start = time.perf_counter()
    segments, info = model.transcribe(
        audio,
        language=config.language,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=100),
        best_of=1,
        beam_size=beam_size,
        temperature=0.0
    )
    text = " ".join(s.text.strip() for s in segments)
    elapsed = (time.perf_counter() - start) * 1000

    return elapsed, text

def main():
    audio, sr = load_audio()
    print(f"Audio duration: {len(audio)/sr:.1f}s\n")

    config = Config.load()
    print(f"Model: {config.model_name}, Device: {config.device_type}, Compute: {config.compute_type}\n")

    beam_sizes = [1, 3, 5, 7]
    results = []

    print("=== ACCURACY vs SPEED TEST ===\n")
    for bs in beam_sizes:
        print(f"Testing beam_size={bs}...")
        try:
            elapsed, text = test_beam_size(bs, audio, sr, config)
            results.append((bs, elapsed, text))
            print(f"  Time: {elapsed/1000:.2f}s ({elapsed:.0f}ms)")
            print(f"  Text length: {len(text)} chars")
            print(f"  Full transcription:\n    {text}\n")
        except Exception as e:
            print(f"  ERROR: {e}\n")

    print("\n=== COMPARISON TABLE ===")
    print(f"{'Beam':<6} {'Time (s)':<10} {'Words':<8} {'Chars':<8}")
    print("-" * 40)
    for bs, elapsed, text in results:
        words = len(text.split())
        print(f"{bs:<6} {elapsed/1000:<10.2f} {words:<8} {len(text):<8}")

if __name__ == "__main__":
    main()
