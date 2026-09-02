"""Regression test: recorder envelope smoothing (direction A + D).

Direction A - attack/release: the level rises FAST when you speak but
   settles SLOWLY when you stop (no abrupt contractions).
Direction D - soft noise floor: below the gate threshold the level tapers
   smoothly toward 0 instead of snapping to 0 (no "pop" on silence).

Tested against AudioRecorder._audio_callback with a stubbed sounddevice.
"""
import sys
import types
from types import SimpleNamespace

import numpy as np

# --- Stub sounddevice so recorder can be imported without hardware ---
sd_stub = types.ModuleType("sounddevice")

def query_devices(device_id=None, kind=None):
    return {"name": "Fake Mic", "default_samplerate": 16000}

class InputStream:
    def __init__(self, *args, **kwargs):
        pass

sd_stub.query_devices = query_devices
sd_stub.InputStream = InputStream
sd_stub.PortAudioError = type("PortAudioError", (Exception,), {})
sys.modules["sounddevice"] = sd_stub

from voice_tui.recorder import AudioRecorder

rec = AudioRecorder.__new__(AudioRecorder)
rec.sample_rate = 16000
rec._recording = True
rec._audio_data = []
rec._current_level = 0.0
rec._peak_level = 0.0
rec._smoothed_level = 0.0
rec._attack_alpha = 0.50
rec._release_alpha = 0.10


def callback(rms_level, blocksize=256):
    """Feed synthetic audio of a given RMS through the level meter."""
    if rms_level <= 0:
        indata = np.zeros((blocksize, 1), dtype=np.float32)
    else:
        indata = np.full((blocksize, 1), rms_level, dtype=np.float32)
    status = None
    rec._audio_callback(indata, blocksize, SimpleNamespace(currentTime=0.0), status)


# Peak-hold/decay fields used by the callback
def level_from_rms(rms):
    """What _audio_callback computes for a constant RMS sine of given amplitude."""
    # rms of a constant array == its value
    if rms > 1e-6:
        db = 20 * np.log10(rms)
        normalized = (db + 50.0) / 50.0
        normalized = min(1.0, max(0.0, normalized))
    else:
        normalized = 0.0
    if normalized < 0.1:
        normalized = normalized * (normalized / 0.1)  # soft knee
    return normalized


# --- D: soft noise floor ---
# A value that maps just under the gate threshold should taper, NOT snap to 0.
# normalized < 0.1 corresponds to roughly -50..-45 dB -> rms ~0.0032..0.0056.
below = 0.004  # -> dB ~ -48 -> normalized ~0.041 -> knee output ~0.017
rec._smoothed_level = 0.0
callback(below)
soft = rec._smoothed_level
assert soft > 0.0, "soft knee: below-threshold audio must NOT snap to 0 (got %f)" % soft
assert soft < level_from_rms(below), "soft knee should attenuate below threshold"
print("OK  D soft noise floor: below-threshold level tapers (%.4f, not 0)" % soft)

# --- A: attack is fast ---
rec._smoothed_level = 0.0
rec._peak_level = 0.0
loud_rms = 0.1  # -> normalized ~0.62
callback(loud_rms)
assert rec._smoothed_level > 0.25, "attack should rise quickly (got %f)" % rec._smoothed_level
loud_est = rec._smoothed_level
print("OK  A attack: rose to %.2f after one loud frame" % loud_est)

# --- A: release is slow ---
callback(0.0)  # silence
after_one = rec._smoothed_level
assert after_one > loud_est * 0.5, "release should retain most height after one silence frame (%f vs %f)" % (after_one, loud_est)
for _ in range(30):
    callback(0.0)
assert rec._smoothed_level < loud_est * 0.4, "release should decay gradually, not vanish (%f)" % rec._smoothed_level
assert rec._smoothed_level >= 0.0
print("OK  A release: after 1 silence frame = %.2f (gentle), after 30 = %.3f" % (after_one, rec._smoothed_level))

print("\nPASS: recorder envelope = fast attack, slow release, soft noise floor")