#!/usr/bin/env python3
"""Sweep beam_size parameter to find optimal latency/accuracy tradeoff for 30s audio."""

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

AUDIO_FILE = "test_30s.wav"

def load_audio():
    audio, sr = sf.read(AUDIO_FILE)
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)
    if audio.dtype != np.float32:
        audio = audio.astype(np.float32)
    return audio, sr

def measure_e2e(transcriber, audio, sample_rate):
    """Measure E2E latency."""
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 / 1024

    start = time.perf_counter()
    text = transcriber.transcribe(audio, sample_rate, skip_formatting=False)
    copy_to_clipboard(text)
    latency = (time.perf_counter() - start) * 1000

    mem_after = process.memory_info().rss / 1024 / 1024
    memory = max(mem_before, mem_after)

    return latency, memory, text

def test_beam_size(beam_size, audio, sr, config):
    """Test a specific beam_size."""
    # Create transcriber with modified beam_size by temporarily patching the class
    class PatchedTranscriber(WhisperTranscriber):
        def transcribe(self, audio, sample_rate=16000, skip_formatting=False):
            # Same as parent but with custom beam_size
            if self._model is None:
                raise TranscriberError("Model not loaded")
            if len(audio) == 0:
                return ""
            try:
                language = self.language
                if language is not None:
                    language = str(language).strip().lower()
                if not language or language in {"auto", "detect", "none"}:
                    language = None

                segments, info = self._model.transcribe(
                    audio,
                    language=language,
                    vad_filter=True,
                    vad_parameters=dict(min_silence_duration_ms=100),
                    best_of=1,
                    beam_size=beam_size,  # OVERRIDE
                    temperature=0.0,
                    initial_prompt="Use proper punctuation, capitalization, and formatting. Use bullet points (•) or numbers (1., 2., 3.) for lists when appropriate."
                )
                transcription = " ".join(segment.text.strip() for segment in segments)
                if not skip_formatting:
                    transcription = self._format_transcription(transcription)
                return transcription.strip()
            except Exception as e:
                raise TranscriberError(f"Transcription failed: {e}")

    # Initialize patched transcriber
    transcriber = PatchedTranscriber(
        model_name=config.model_name,
        language=config.language,
        device=config.device_type,
        compute_type=config.compute_type
    )

    # Warm up with short audio
    warm = audio[:int(sr * 0.5)]
    _ = transcriber.transcribe(warm, sr, skip_formatting=True)

    # Measure 3 runs
    latencies = []
    texts = []
    for i in range(3):
        lat, mem, txt = measure_e2e(transcriber, audio, sr)
        latencies.append(lat)
        texts.append(txt)

    median_lat = sorted(latencies)[len(latencies)//2]
    return median_lat, texts[0], mem

def main():
    audio, sr = load_audio()
    print(f"Audio: {len(audio)/sr:.1f}s", file=sys.stderr)

    config = Config.load()
    print(f"Model: {config.model_name}", file=sys.stderr)

    beam_sizes = [1, 3, 5, 7, 10]
    results = []

    print("\nBeam Size Sweep for 30-second audio:\n", file=sys.stderr)
    for bs in beam_sizes:
        print(f"Testing beam_size={bs}...", file=sys.stderr)
        try:
            lat, text, mem = test_beam_size(bs, audio, sr, config)
            results.append((bs, lat, len(text), mem))
            print(f"  Result: {lat:.1f}ms, text_len={len(text)}, mem={mem:.1f}MB", file=sys.stderr)
            print(f"  Sample: {text[:100]}...", file=sys.stderr)
        except Exception as e:
            print(f"  ERROR: {e}", file=sys.stderr)

    print("\n=== SUMMARY ===", file=sys.stderr)
    print("Beam  Latency(ms)  TextLen  Memory", file=sys.stderr)
    for bs, lat, txtlen, mem in results:
        print(f"{bs:4d}  {lat:10.1f}  {txtlen:7d}  {mem:.1f}", file=sys.stderr)

    # Also output METRIC for autoresearch (use best latency)
    if results:
        best = min(results, key=lambda x: x[1])
        print(f"\nMETRIC e2e_latency={best[1]:.1f}")
        print(f"METRIC peak_memory={best[3]:.1f}")

if __name__ == "__main__":
    main()
