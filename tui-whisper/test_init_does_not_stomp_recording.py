"""Regression test: background init must not stomp an active recording status.

Bug: _init_background() ran set_status("idle", "Ready") unconditionally when
startup init finished. On Windows, heavy imports make init take ~12-14s, so if
the user started recording before init completed, the UI flipped to
\"READY TO RECORD\" mid-hold (and the waveform froze) even though recording
continued. Same guard as _on_model_loaded already has.
"""
import sys
import types

# --- Hermetic stubs ---
fk = types.ModuleType("keyboard")
fk.hook = lambda cb: None
fk.unhook_all = lambda: None
fk.is_pressed = lambda n: False
fk.add_hotkey = lambda *a, **k: None
sys.modules["keyboard"] = fk

from voice_tui.main import VoiceToTextController


class FakeApp:
    def __init__(self):
        self.current_status = "recording"  # user is mid-hold
        self.calls = []

    def set_status(self, status, message=""):
        self.calls.append((status, message))
        self.current_status = status

    def show_error(self, msg):
        self.calls.append(("error", msg))

    def call_from_thread(self, fn, *a, **k):
        fn(*a, **k)

    def rehook_ui_keys(self):
        return True


class FakeConfig:
    model_name = "base"
    language = "en"
    hotkey = "ctrl+shift+z"
    sample_rate = 16000
    min_recording_duration = 0.5
    device_type = "auto"
    compute_type = "auto"
    auto_type = False
    auto_paste = True
    type_interval = 0.01
    use_smart_formatting = False
    openrouter_api_key = ""
    openrouter_model = "qwen/qwen-2.5-7b-instruct"

    def save(self):
        pass


# Case 1: init completes while recording -> status must NOT change
ctrl = VoiceToTextController(FakeConfig())
ctrl.app = FakeApp()
ctrl.app.current_status = "recording"
ctrl.transcriber = types.SimpleNamespace(is_loaded=True)
ctrl.initialize = lambda: True  # stub - no hardware on dev box

ctrl._init_background()
assert ctrl.app.current_status == "recording", "must stay recording, got %r" % ctrl.app.current_status
assert not any(s == "idle" for s, _ in ctrl.app.calls), "must not flip to idle: %r" % ctrl.app.calls
print("OK  init completing during recording keeps recording status")

# Case 2: init completes while processing -> must not change
ctrl2 = VoiceToTextController(FakeConfig())
ctrl2.app = FakeApp()
ctrl2.app.current_status = "processing"
ctrl2.transcriber = types.SimpleNamespace(is_loaded=True)
ctrl2.initialize = lambda: True
ctrl2._init_background()
assert ctrl2.app.current_status == "processing"
print("OK  init completing during processing keeps processing status")

# Case 3: init completes while idle -> sets Ready
ctrl3 = VoiceToTextController(FakeConfig())
ctrl3.app = FakeApp()
ctrl3.app.current_status = "idle"
ctrl3.transcriber = types.SimpleNamespace(is_loaded=True)
ctrl3.initialize = lambda: True
ctrl3._init_background()
assert ("idle", "Ready") in ctrl3.app.calls, "idle status should become Ready: %r" % ctrl3.app.calls
print("OK  init completing while idle shows Ready")

print("\nPASS: status never stomped mid-recording")