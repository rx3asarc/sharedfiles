"""Regression test: holding the hotkey must not write anything to the terminal.

Previously _on_hotkey_press/_on_hotkey_release wrote "[PRESS] ...\\n" to
sys.stderr on EVERY key-repeat event while the hotkey was held. Each newline
scrolled the TUI up one line; the 10 FPS redraw snapped it back -> screen
shaking/wobbling exactly while recording.

This test captures sys.stderr and asserts:
  1. Press/release handlers write nothing to the terminal.
  2. Key-repeat presses while recording are ignored (recorder starts once).
"""
import io
import sys
import types

# --- Hermetic stubs: this box has no sounddevice/faster_whisper ---
# voice_tui.main imports these at module load; stub them so the test
# can exercise the controller logic without hardware deps.
def _stub_module(name, names):
    mod = types.ModuleType(name)
    for n in names:
        setattr(mod, n, type(n, (), {}))
    sys.modules[name] = mod

_stub_module("voice_tui.recorder", ["AudioRecorder", "NoMicrophoneError", "AudioRecorderError"])
_stub_module("voice_tui.transcriber", ["WhisperTranscriber", "ModelLoadError", "TranscriberError"])
_stub_module("voice_tui.auto_type", ["AutoTyper"])

# --- Fake keyboard with controllable press-state ---
fake_keyboard = types.ModuleType("keyboard")
fake_keyboard._state = {}

def is_pressed(name):
    if name == "control":
        name = "ctrl"
    return fake_keyboard._state.get(name, False)

fake_keyboard.is_pressed = is_pressed
fake_keyboard.hook = lambda cb: None
fake_keyboard.unhook_all = lambda: None
fake_keyboard.add_hotkey = lambda *a, **k: None
sys.modules["keyboard"] = fake_keyboard

from voice_tui.main import VoiceToTextController

# --- Capture every write the handlers make to the terminal ---
class TerminalSpy(io.TextIOBase):
    def __init__(self):
        self.writes = []

    def write(self, s):
        self.writes.append(s)
        return len(s)

    def flush(self):
        pass

spy = TerminalSpy()
original_stderr = sys.stderr
sys.stderr = spy

try:
    # --- Minimal fakes so the handlers don't touch hardware ---
    class FakeRecorder:
        def __init__(self):
            self.is_recording = False
            self.start_calls = 0
            self.stop_calls = 0

        def start_recording(self):
            self.start_calls += 1
            self.is_recording = True

        def stop_recording(self):
            self.stop_calls += 1
            self.is_recording = False

    class FakeConfig:
        pass

    ctrl = VoiceToTextController(FakeConfig())
    ctrl.recorder = FakeRecorder()
    ctrl.start_recording = ctrl.recorder.start_recording
    ctrl.stop_recording = ctrl.recorder.stop_recording
    ctrl._hotkey_key = "z"
    ctrl._hotkey_modifiers = {"ctrl", "shift"}

    # 1. First press (starts recording) - combo held
    fake_keyboard._state = {"ctrl": True, "shift": True, "z": True}
    ctrl._on_hotkey_press()
    assert ctrl.recorder.start_calls == 1, "first press should start recording"
    assert ctrl._hotkey_active, "controller should be active while held"

    # 2. Simulate 50 OS key-repeat events while still holding (the old bug path)
    for _ in range(50):
        ctrl._on_hotkey_press()
    assert ctrl.recorder.start_calls == 1, "key repeats must not restart recording"
    assert ctrl.recorder.is_recording, "still recording"

    # 2b. Spurious 'up' events while STILL HELD must not cancel recording
    for _ in range(10):
        ctrl._on_hotkey_release()  # fake state still has combo down
    assert ctrl.recorder.stop_calls == 0, "spurious ups must not stop recording"
    assert ctrl.recorder.is_recording, "still recording after spurious ups"

    # 3. Real release (keys now up)
    fake_keyboard._state = {"ctrl": False, "shift": False, "z": False}
    ctrl._on_hotkey_release()
    assert ctrl.recorder.stop_calls == 1, "release should stop recording"
    assert not ctrl._hotkey_active, "controller should be inactive after release"
    assert not ctrl.recorder.is_recording, "recorder should be stopped"

    # 4. Release without prior press (spurious) must not crash or write
    ctrl._on_hotkey_release()

    # 5. THE assertion: nothing was ever written to the terminal
    terminal_output = ''.join(spy.writes)
    assert terminal_output == "", "handler wrote to terminal: %r" % terminal_output[:200]
    assert "PRESS" not in terminal_output and "RELEASE" not in terminal_output

    print("PASS: no terminal writes during press/release; key-repeat ignored")
finally:
    sys.stderr = original_stderr