"""Regression test: startup must not block on Whisper model load.

Previously WhisperTranscriber.__init__ loaded the model synchronously, which
made `voice-tui` take many seconds to show the TUI. Now:
  - Construction is instant (no model load).
  - start_background_load() loads in a daemon thread.
  - transcribe() called before the model is ready waits, then works.
  - A background load failure surfaces via on_error and transcribe() raises.

faster_whisper is stubbed with a deliberately SLOW model to prove the
constructor returns before the model is done.
"""
import sys
import time
import types
from types import SimpleNamespace

# --- Stub faster_whisper with a slow fake model ---
FAKE_LOAD_SECONDS = 0.4


class _FakeSeg:
    text = "hello world"


class _FakeModel:
    def __init__(self, model_name, device="cpu", compute_type="int8"):
        if model_name == "broken":
            raise RuntimeError("simulated load failure")
        time.sleep(FAKE_LOAD_SECONDS)  # deliberately slow
        self._name = model_name

    def transcribe(self, audio, **kwargs):
        return ([_FakeSeg()], None)


stub = types.ModuleType("faster_whisper")
stub.WhisperModel = _FakeModel
sys.modules["faster_whisper"] = stub

import numpy as np
from voice_tui.transcriber import WhisperTranscriber, TranscriberError

SILENCE = np.zeros(16000, dtype=np.float32)

# 1. Construction must be near-instant (no model load)
t0 = time.monotonic()
tr = WhisperTranscriber(model_name="tiny", language="en", device="cpu", compute_type="int8")
elapsed = time.monotonic() - t0
assert tr._model is None, "model must not be loaded at construction"
assert elapsed < 0.2, "constructor must not block on model load (took %.2fs)" % elapsed
print("OK  construction instant (%.3fs), model not yet loaded" % elapsed)

# 2. Background load + on_loaded callback
loaded = []
tr.start_background_load(on_loaded=lambda: loaded.append(True))
assert tr._load_started, "background load should be started"
assert tr._model is None, "model should still be loading (background)"
t0 = time.monotonic()
tr.ensure_loaded()
wait = time.monotonic() - t0
assert tr.is_loaded, "model should be loaded after ensure_loaded"
assert loaded == [True], "on_loaded callback should have fired"
print("OK  background load completed (waited %.2fs for ensure_loaded)" % wait)

# 3. transcribe() immediately after start (before model ready) must wait then work
tr2 = WhisperTranscriber(model_name="tiny", language="en", device="cpu", compute_type="int8")
tr2.start_background_load()
t0 = time.monotonic()
text = tr2.transcribe(SILENCE, 16000)
t_total = time.monotonic() - t0
assert text == "Hello world", "expected formatted text, got %r" % text
assert t_total >= FAKE_LOAD_SECONDS - 0.05, "transcribe should have waited for the model"
print("OK  early transcribe waited for model (%.2fs) and returned: %r" % (t_total, text))

# 4. Background load failure -> on_error + transcribe raises
errors = []
tr3 = WhisperTranscriber(model_name="broken", language="en", device="cpu", compute_type="int8")
tr3.start_background_load(on_error=lambda e: errors.append(e))
try:
    tr3.ensure_loaded()
    raise AssertionError("ensure_loaded should raise when model failed to load")
except TranscriberError:
    pass
assert errors, "on_error should have fired"
try:
    tr3.transcribe(SILENCE, 16000)
    raise AssertionError("transcribe should raise when model failed to load")
except TranscriberError:
    pass
print("OK  background load failure surfaces via on_error + TranscriberError")

print("\nPASS: startup no longer blocks on model load")