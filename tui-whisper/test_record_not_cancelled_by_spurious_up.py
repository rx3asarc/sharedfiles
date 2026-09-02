"""Regression test: spurious 'up' events must NOT cancel a held recording.

Windows 'keyboard' can emit an 'up' event for the hotkey character during
key-repeat or modifier flicker while the user is STILL holding the combo.
Previously _on_hotkey_release() stopped the recording on ANY up event ->
recordings cancelled mid-hold (exactly what the user saw).

Fix: only a CONFIRMED release (hotkey key AND all modifiers actually up)
stops the recording. Spurious ups while held are ignored.
"""
import io
import sys
import types


class FakeKeyboard(types.ModuleType):
    """Keyboard stub where press state is controllable per key."""

    def __init__(self):
        super().__init__("keyboard")
        self._state = {}  # key_name -> bool pressed
        self._hooks = []

    def is_pressed(self, name):
        # Accept aliases used by the app
        if name in ("control",):
            name = "ctrl"
        return self._state.get(name, False)

    def hook(self, cb):
        self._hooks.append(cb)
        return cb

    def unhook_all(self):
        self._hooks.clear()

    def add_hotkey(self, *a, **k):
        pass


fk = FakeKeyboard()
sys.modules["keyboard"] = fk

# --- Hermetic stubs so main imports cleanly ---
import voice_tui.main as m

# Stub out the heavy modules before main is imported? main now lazy-imports them,
# so importing main itself is light. Good.

from voice_tui.main import VoiceToTextController


class FakeConfig:
    hotkey = "ctrl+shift+z"
    model_name = "base"
    language = "en"
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


class FakeRecorder:
    def __init__(self):
        self.is_recording = False
        self.stops = 0
        self.starts = 0

    def start_recording(self):
        self.starts += 1
        self.is_recording = True

    def stop_recording(self):
        self.stops += 1
        self.is_recording = False


ctrl = VoiceToTextController(FakeConfig())
ctrl.recorder = FakeRecorder()
ctrl._hotkey_key = "z"
ctrl._hotkey_modifiers = {"ctrl", "shift"}

# --- Scenario: user holds ctrl+shift+z ---
fk._state = {"ctrl": True, "shift": True, "z": True}

# Press (starts recording)
ctrl._on_hotkey_press()
assert ctrl.recorder.is_recording and ctrl.recorder.starts == 1
assert ctrl._hotkey_active

# Spurious ups WHILE held (what Windows does on repeat / modifier flicker)
for _ in range(5):
    ctrl._on_hotkey_release()
# Key repeat can also fire 'down' again - that's fine (guard handles it)
for _ in range(5):
    ctrl._on_hotkey_press()

# MUST still be recording
assert ctrl.recorder.is_recording, "spurious ups cancelled the recording!"
assert ctrl.recorder.stops == 0, "recording must not stop while combo held"
assert ctrl._hotkey_active, "must stay active while held"
print("OK  spurious ups while held do NOT cancel recording")

# --- Real release: user lets go ---
fk._state = {"ctrl": False, "shift": False, "z": False}
ctrl._on_hotkey_release()
assert not ctrl.recorder.is_recording, "real release SHOULD stop recording"
assert ctrl.recorder.stops == 1, "exactly one stop on real release"
assert not ctrl._hotkey_active
print("OK  real release stops recording exactly once")

print("\nPASS: recordings no longer cancelled by spurious key-up events")