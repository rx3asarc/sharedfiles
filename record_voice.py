#!/usr/bin/env python3
"""Record audio from microphone and save as WAV.

Press Enter to start recording, then speak. Press Enter again when done.
Or use fixed duration with --duration flag.
"""

import sys
import numpy as np
import sounddevice as sd
from pathlib import Path
import argparse

def list_microphones():
    """List available input devices."""
    print("Available audio input devices:", file=sys.stderr)
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            print(f"  {i}: {dev['name']} (inputs: {dev['max_input_channels']})", file=sys.stderr)

def record_audio(duration_sec=30.0, sample_rate=16000, channels=1):
    """Record audio from microphone for a fixed duration.

    Args:
        duration_sec: Recording duration in seconds
        sample_rate: Sample rate
        channels: Number of channels (1 for mono)

    Returns:
        audio array (float32) and sample rate
    """
    print(f"Recording for {duration_sec} seconds...", file=sys.stderr)
    print("Start speaking now...", file=sys.stderr)
    audio = sd.rec(
        int(duration_sec * sample_rate),
        samplerate=sample_rate,
        channels=channels,
        dtype=np.float32
    )
    sd.wait()
    print("Recording complete.", file=sys.stderr)
    return audio.flatten(), sample_rate

def save_wav(audio, sample_rate, filename):
    """Save audio to WAV file."""
    import wave
    # Convert to int16 for WAV
    audio_int16 = (audio * 32767).astype(np.int16)

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # mono
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())

    print(f"Saved audio to: {filename}", file=sys.stderr)
    print(f"Duration: {len(audio)/sample_rate:.2f} seconds", file=sys.stderr)
    print(f"RMS level: {np.sqrt(np.mean(audio**2)):.3f}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Record audio from microphone")
    parser.add_argument("--duration", type=float, help="Fixed recording duration in seconds")
    parser.add_argument("--output", default="test_30s.wav", help="Output WAV filename")
    parser.add_argument("--list-devices", action="store_true", help="List available input devices")
    args = parser.parse_args()

    if args.list_devices:
        list_microphones()
        return 0

    # Check default device
    try:
        device_info = sd.query_devices(kind='input')
        print(f"Using input device: {device_info['name']}", file=sys.stderr)
    except Exception as e:
        print(f"Error querying input device: {e}", file=sys.stderr)
        print("Run with --list-devices to see available inputs", file=sys.stderr)
        return 1

    # Record
    try:
        audio, sr = record_audio(duration_sec=args.duration, sample_rate=16000)
    except Exception as e:
        print(f"Recording error: {e}", file=sys.stderr)
        return 1

    if len(audio) == 0:
        print("No audio recorded.", file=sys.stderr)
        return 1

    # Save
    save_wav(audio, sr, args.output)

    return 0

if __name__ == "__main__":
    sys.exit(main())
