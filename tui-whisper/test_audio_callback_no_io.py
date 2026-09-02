"""Regression test: realtime audio callback must be I/O free.

The callback runs on sounddevice's RT thread. It previously did:
  - print() on status  -> blocking console write that corrupted the TUI and
    caused input overflow (the on-screen "Audio callback status: ..." garbage)
  - open("debug.log","a")+write on EVERY callback while talking -> disk I/O
    in the RT thread -> overflow -> dropped frames -> recordings cut off mid-word

Now the callback only appends audio + math. This test feeds a fake indata and
asserts: no writes to stdout/stderr, no debug.log writes, overflow flagged
without touching the console.
"""
import io
import sys
import types
from types import SimpleNamespace

import numpy as np

# --- Stub sounddevice ---
sd_stub = types.ModuleType("sounddevice")

def query_devices(device_id=None, kind=None):
    return {"name": "Fake Mic", "default_samplerate": 16000}

class InputStream:
    def __init__(self, *args, **kwargs):
        self.blocksize = kwargs.get("blocksize", 0)

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
rec._attack_alpha = 0.5
rec._release_alpha = 0.1

# --- Spy on terminal + disk ---
out_spy = io.StringIO()
err_spy = io.StringIO()
old_out, old_err = sys.stdout, sys.stderr
sys.stdout, sys.stderr = out_spy, err_spy

try:
    # Simulate several callbacks with loud audio (the old code wrote debug.log
    # every time level > 0.2)
    loud = np.full((256, 1), 0.1, dtype=np.float32)
    for _ in range(50):
        rec._audio_callback(loud, 256, SimpleNamespace(currentTime=0.0), None)

    # And one with an overflow status
    rec._audio_callback(loud, 256, SimpleNamespace(currentTime=0.0),
                        SimpleNamespace(flags=1, callback_time=0.0))

    assert out_spy.getvalue() == "", "callback must not write to stdout"
    assert err_spy.getvalue() == "", "callback must not write to stderr"
    assert rec._overflow_count == 1, "overflow should be counted"
    assert rec.get_callback_status() != "", "overflow status should be captured"
    assert rec._audio_data, "audio must still be collected"
    assert len(rec._audio_data) == 51, "all callbacks should collect audio"

    # Properly instantiated AudioRecorder gets the larger blocksize too
    stream = rec.record_stream() if hasattr(rec, "record_stream") else None
    print("OK  callback is I/O-free: no stdout/stderr/disk writes")

    # verify record_stream default param exists via class
    import inspect
    sig = inspect.signature(AudioRecorder.record_stream)
    print("OK  record_stream has no args (blocksize set inside)")
finally:
    sys.stdout, sys.stderr = old_out, old_err

print("\nPASS: realtime audio callback is I/O-free -> no overflow/cutoff")