#!/usr/bin/env python3
"""Profile 30-second transcription to find bottlenecks."""

import sys
import time
import numpy as np
import psutil
import os
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

def profile_transcription(transcriber, audio, sample_rate):
    """Profile the transcription pipeline."""
    print("\n=== Profiling 30s Transcription ===")

    # Time just the model.transcribe call
    print("1. Timing model.transcribe()...")
    start = time.perf_counter()
    segments, info = transcriber._model.transcribe(
        audio,
        language=transcriber.language,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=100),
        best_of=1,
        beam_size=7,
        temperature=0.0
    )
    # Consume segments (force iteration)
    text = " ".join(s.text.strip() for s in segments)
    transcribe_time = (time.perf_counter() - start) * 1000
    print(f"   model.transcribe: {transcribe_time:.1f}ms")
    print(f"   Text length: {len(text)} chars")

    # Time VAD separately? Can't easily separate, but we can test without VAD
    print("\n2. Testing without VAD...")
    start = time.perf_counter()
    segments_novad, info = transcriber._model.transcribe(
        audio,
        language=transcriber.language,
        vad_filter=False,
        best_of=1,
        beam_size=7,
        temperature=0.0
    )
    text_novad = " ".join(s.text.strip() for s in segments_novad)
    novad_time = (time.perf_counter() - start) * 1000
    print(f"   Without VAD: {novad_time:.1f}ms (VAD overhead: {transcribe_time - novad_time:.1f}ms)")

    # Time different beam_size values
    print("\n3. Testing beam_size impact...")
    for bs in [1, 3, 5, 7, 10]:
        start = time.perf_counter()
        segs, info = transcriber._model.transcribe(
            audio,
            language=transcriber.language,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=100),
            best_of=1,
            beam_size=bs,
            temperature=0.0
        )
        _ = " ".join(s.text.strip() for s in segs)
        t_bs = (time.perf_counter() - start) * 1000
        print(f"   beam_size={bs}: {t_bs:.1f}ms")

    # Time compute_type impact (we'd need to reload model)
    print("\n4. Checking model info...")
    info = transcriber.get_model_info()
    print(f"   Model: {info['model_name']}, Device: {info['device']}, Compute: {info['compute_type']}")

    # Estimate per-second throughput
    duration = len(audio) / sample_rate
    throughput = duration / (transcribe_time/1000)
    print(f"\nThroughput: {throughput:.2f}x real-time")
    print(f"  (Processed {duration:.1f}s of audio in {transcribe_time/1000:.1f}s)")

def main():
    audio, sr = load_audio()
    print(f"Loaded audio: {len(audio)/sr:.1f}s, sample_rate={sr}")

    config = Config.load()
    transcriber = WhisperTranscriber(
        model_name=config.model_name,
        language=config.language,
        device=config.device_type,
        compute_type=config.compute_type
    )

    profile_transcription(transcriber, audio, sr)

if __name__ == "__main__":
    main()
