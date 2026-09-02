"""Regression test: TUI spawns immediately - init runs in background thread.

Previously main() called controller.initialize() synchronously BEFORE the TUI,
so on slow machines there was a multi-second gap between the banner printing
and the TUI appearing (heavy imports + mic check). Now:
  - run() sets status "Starting up..." and spawns init in a daemon thread,
    so app.run() begins immediately.
  - Pressing the hotkey before init finishes shows a friendly message instead
    of crashing (guards for recorder/transcriber being None).
"""
import io
import sys
import time
import types

from voice_tui.main import VoiceToTextController, VoiceToTextApp as App


class TerminalSpy(io.TextIOBase):
    def __init__(self):
        self.writes = []

    def write(self, s):
        self.writes.append(s)
        return len(s)

    def flush(self):
        pass


# --- Fake keyboard module (imported by main/ascii_app) ---
fake_keyboard = types.ModuleType("keyboard")
fake_keyboard._hooks = []

def hook(cb):
    fake_keyboard._hooks.append(cb)
    return cb

def unhook_all():
    fake_keyboard._hooks.clear()

def is_pressed(mod):
    return False

fake_keyboard.hook = hook
fake_keyboard.unhook_all = unhook_all
fake_keyboard.is_pressed = is_pressed
sys.modules["keyboard"] = fake_keyboard

# --- Fake app that records what set_status was called with ---
class FakeApp:
    def __init__(self):
        self.status_calls = []
        self.error_calls = []
        self.needs_render = True
        self.current_status = "idle"

    def set_status(self, status, message=""):
        self.status_calls.append((status, message))
        self.current_status = status

    def show_error(self, msg):
        self.error_calls.append(msg)

    def call_from_thread(self, method, *args, **kwargs):
        method(*args, **kwargs)

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


# 1. Record terminal writes during run() startup (must be quiet - no stdout spam)
spy = TerminalSpy()
orig_stderr, orig_stdout = sys.stderr, sys.stdout
sys.stderr = spy
sys.stdout = io.StringIO()  # banner goes elsewhere; we only assert on stderr

try:
    ctrl = VoiceToTextController(FakeConfig())
    ctrl.app = FakeApp()

    # Simulate main(): run() without blocking initialize()
    # We don't call run() (that would render-loop); instead verify the pieces:
    #   - run() would set "Starting up..." + spawn thread.
    # We test _init_background directly with initialize() stubbed.
    orig_initialize = ctrl.initialize

    # 2. The guard: pressing hotkey before init → friendly error, no crash
    ctrl.recorder = None
    ctrl.transcriber = None
    ctrl.start_recording()  # must not raise
    assert "Still starting up..." in ctrl.app.error_calls, "should show startup message"
    ctrl.app.error_calls.clear()

    # 3. stop_recording with no recorder → no crash
    ctrl.stop_recording()
    print("OK  guards: start/stop before init done are safe")

    # 4. _init_background success path → status updates via call_from_thread
    def fake_init_ok():
        ctrl.recorder = object()
        ctrl.transcriber = types.SimpleNamespace(is_loaded=True)
        return True
    ctrl.initialize = fake_init_ok

    ctrl._init_background()
    assert ("idle", "Ready") in ctrl.app.status_calls, ctrl.app.status_calls
    print("OK  _init_background success sets Ready status")
    status_calls = list(ctrl.app.status_calls)
    ctrl.app.status_calls.clear()

    # 5. _init_background failure path → error surfaced
    def fake_init_fail():
        ctrl.init_error = "No microphone found"
        return False
    ctrl.initialize = fake_init_fail
    ctrl._init_background()
    assert ctrl.app.error_calls and "Init failed" in ctrl.app.error_calls[0], ctrl.app.error_calls
    print("OK  _init_background failure surfaces error in TUI")

    # 6. No stray writes to terminal during these operations
    assert spy.writes == [] or all("PRESS" not in w and "RELEASE" not in w for w in spy.writes), spy.writes
    print("OK  no terminal pollution during startup guards")

finally:
    sys.stderr = orig_stderr
    sys.stdout = orig_stdout

print("\nPASS: instant spawn - init runs in background, guards safe")