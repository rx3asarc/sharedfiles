#!/usr/bin/env python3
"""Record 30 seconds of audio and save to WAV file."""

import sys
import numpy as np
import sounddevice as sd
from pathlib import Path

def record_audio(duration_sec=30.0, sample_rate=16000):
    """Record audio from microphone."""
    print(f"Recording {duration_sec} seconds of audio...")
    print("Speak naturally. Press Ctrl+C to cancel early.", file=sys.stderr)

    try:
        # Record
        audio = sd.rec(
            int(duration_sec * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype=np.float32
        )
        sd.wait()  # Wait for recording to complete
        print("Recording complete.", file=sys.stderr)
    except KeyboardInterrupt:
        print("\nRecording cancelled by user.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Recording failed: {e}", file=sys.stderr)
        return None

    # Flatten to mono (already mono)
    audio = audio.flatten()
    return audio, sample_rate

def save_wav(audio, sample_rate, filename):
    """Save audio to WAV file."""
    import wave
    # Convert to int16 for WAV
    audio_int16 = (audio * 32767).astype(np.int16)

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())

    print(f"Saved to {filename}")

def main():
    print("=== 30-Second Audio Recorder ===")
    audio_data = record_audio(duration_sec=30.0, sample_rate=16000)
    if audio_data is None:
        return 1

    audio, sample_rate = audio_data

    # Save to file in current directory
    filename = "test_30s.wav"
    save_wav(audio, sample_rate, filename)

    # Also show RMS level
    rms = np.sqrt(np.mean(audio**2))
    print(f"Audio RMS: {rms:.3f} (should be ~0.1 for normal speech)")
    print(f"Peak: {np.max(np.abs(audio)):.3f}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
