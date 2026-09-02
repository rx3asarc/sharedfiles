"""Regression test: settings improvements.

1. Hotkey modifier-chord capture (Alt+Ctrl): pressing a SECOND modifier while
   one is held commits a modifier-only chord like ctrl+alt, and config
   validation accepts it (persists across launches).
2. Tab-cycling for bool/choice settings: Tab toggles True/False or cycles
   model names; Enter saves; no text typing needed.
3. Modifier+key capture still works (ctrl+alt+x).
"""
import sys
import types


class FakeKeyboard(types.ModuleType):
    def __init__(self):
        super().__init__("keyboard")
        self._state = {}
        self._hooks = []

    def is_pressed(self, name):
        if name == "control":
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

from voice_tui.ascii_app import VoiceToTextASCIIApp
from voice_tui.config import Config


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


class FakeController:
    def __init__(self):
        self.config = FakeConfig()
        self.reconfigured = []
        self._last_save_error = None

    def reconfigure_hotkey(self, hk):
        self.reconfigured.append(hk)
        self.config.hotkey = hk


# ===== 1. Modifier-chord capture: Ctrl then Alt commits ctrl+alt =====
ctrl = FakeController()
app = VoiceToTextASCIIApp(FakeConfig(), ctrl)
app.in_hotkey_capture = True

fk._state = {"ctrl": True}
app._handle_hotkey_capture_key("ctrl")   # first modifier - waiting
assert app.in_hotkey_capture, "first modifier alone shouldn't commit"
assert ctrl.reconfigured == []

fk._state = {"ctrl": True, "alt": True}
app._handle_hotkey_capture_key("alt")    # second modifier - commit chord
assert not app.in_hotkey_capture, "second modifier should commit the chord"
assert ctrl.reconfigured == ["alt+ctrl"], "should commit ctrl+alt chord: %r" % ctrl.reconfigured
print("OK  1. modifier-chord capture: Ctrl+Alt commits %r" % ctrl.reconfigured)

# ===== 2. Config validation accepts modifier-only chords =====
ok = Config._validate_hotkey("ctrl+alt")
assert ok == "ctrl+alt", "should accept modifier chord, got %r" % ok
ok2 = Config._validate_hotkey("shift+win")
assert ok2 == "shift+win"
# Still rejects garbage
assert Config._validate_hotkey("h+ctrl") == FakeConfig.hotkey  # non-modifier 'h'
print("OK  2. config validation accepts modifier-only chords, rejects garbage")

# ===== 3. Modifier+key capture still works =====
ctrl3 = FakeController()
app3 = VoiceToTextASCIIApp(FakeConfig(), ctrl3)
app3.in_hotkey_capture = True
fk._state = {"ctrl": True, "alt": True, "x": True}
app3._handle_hotkey_capture_key("x")
assert ctrl3.reconfigured == ["alt+ctrl+x"], ctrl3.reconfigured
print("OK  3. modifier+key capture still works")

# ===== 4. Tab cycles boolean settings =====
ctrl4 = FakeController()
app4 = VoiceToTextASCIIApp(FakeConfig(), ctrl4)

# Navigate: cursor 0=Model ... 7=Auto Type (bool)
# Let's directly enter edit on Auto Type (index 7)
app4.settings_mode = True
app4.settings_cursor = 7  # Auto Type
app4._handle_settings_navigation_key("e")
assert app4.settings_editing, "should be editing Auto Type"
assert app4.settings_edit_buffer.strip() == "False", "buffer=%r" % app4.settings_edit_buffer

app4._handle_settings_edit_key("tab")  # toggle -> True
assert app4.settings_edit_buffer == "True", "tab should toggle bool to True, got %r" % app4.settings_edit_buffer
app4._handle_settings_edit_key("tab")  # toggle -> False
assert app4.settings_edit_buffer == "False"
print("OK  4. Tab toggles boolean setting (False->True->False)")

# Enter saves
app4._handle_settings_edit_key("enter")
assert not app4.settings_editing
assert getattr(ctrl4.config, "auto_type") is False, "enter should save current bool"

# ===== 5. Tab cycles choice settings (Model) =====
app5 = VoiceToTextASCIIApp(FakeConfig(), FakeController())
app5.settings_mode = True
app5.settings_cursor = 0  # Model (choice)
app5._handle_settings_navigation_key("e")
assert app5.settings_edit_buffer == "base"
app5._handle_settings_edit_key("tab")   # cycle base -> small
assert app5.settings_edit_buffer == "small", "tab should cycle model base->small, got %r" % app5.settings_edit_buffer
app5._handle_settings_edit_key("enter")
assert app5.controller.config.model_name == "small", "enter should save cycled choice"
print("OK  5. Tab cycles choice setting (base->small, enter saves)")

# ===== 4. Typing is blocked for bool/choice (no Truee) =====
app6 = VoiceToTextASCIIApp(FakeConfig(), FakeController())
app6.settings_mode = True
app6.settings_cursor = 7  # Auto Type (bool)
app6._handle_settings_navigation_key("e")
assert app6.settings_edit_buffer == "False"
app6._handle_settings_edit_key("e")  # try typing - should be BLOCKED
assert app6.settings_edit_buffer == "False", "typing must not append for bool, got %r" % app6.settings_edit_buffer
assert "Tab" in app6.settings_message, "should hint to use Tab"
app6._handle_settings_edit_key("tab")  # Tab still works
app6._handle_settings_edit_key("e")  # typing still blocked after Tab
assert app6.settings_edit_buffer == "True", "buffer should stay exactly 'True' (no Truee), got %r" % app6.settings_edit_buffer

# Choice also blocks typing
app7 = VoiceToTextASCIIApp(FakeConfig(), FakeController())
app7.settings_mode = True
app7.settings_cursor = 0  # Model (choice)
app7._handle_settings_navigation_key("e")
app7._handle_settings_edit_key("x")
assert app7.settings_edit_buffer == "base", "typing must not corrupt choice, got %r" % app7.settings_edit_buffer

# Text fields still allow typing
app8 = VoiceToTextASCIIApp(FakeConfig(), FakeController())
app8.settings_mode = True
app8.settings_cursor = 1  # Language (string)
app8._handle_settings_navigation_key("e")
app8._handle_settings_edit_key("e")
assert app8.settings_edit_buffer == "ene", "text fields still allow typing, got %r" % app8.settings_edit_buffer
print("OK  4. typing blocked for bool/choice; text fields still allow typing")

print("\nPASS: modifier-chord hotkey + Tab-cycling for bool/choice")