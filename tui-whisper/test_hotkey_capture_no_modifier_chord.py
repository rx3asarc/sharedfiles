"""Regression test: hotkey capture must not commit a modifier-chord.

Bug: pressing the SECOND modifier (e.g. Alt while Ctrl held) committed
\"ctrl+alt\" as the hotkey because the modifier-exclusion only removed the
pressed modifier, leaving the other held modifiers non-empty. \"ctrl+alt\"
fails _validate_hotkey on next launch (final part is a modifier) so the
hotkey silently reset to default - user had to re-capture every session.

Fix: pure modifier presses are waiting states; only a NON-modifier key
(with >=1 modifier held) commits.
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


class FakeConfig:
    hotkey = "ctrl+shift+z"


class FakeController:
    def __init__(self):
        self.config = FakeConfig()
        self.reconfigured = []
        self._last_save_error = None

    def reconfigure_hotkey(self, hk):
        self.reconfigured.append(hk)
        self.config.hotkey = hk


ctrl = FakeController()
app = VoiceToTextASCIIApp(FakeConfig(), ctrl)
app.in_hotkey_capture = True

# User presses Ctrl, then Alt (two modifiers) - must NOT commit
fk._state = {"ctrl": True}
app._handle_hotkey_capture_key("ctrl")
assert app.in_hotkey_capture, "ctrl press must not exit capture"
assert ctrl.reconfigured == [], "modifier press must not commit a hotkey"

fk._state = {"ctrl": True, "alt": True}
app._handle_hotkey_capture_key("alt")
assert app.in_hotkey_capture, "alt press must not exit capture"
assert ctrl.reconfigured == [], "second modifier must not commit (was the bug: 'ctrl+alt')"
print("OK  modifiers alone never commit")

# Shift + real key -> commits
fk._state = {"shift": True}
app._handle_hotkey_capture_key("shift")
assert ctrl.reconfigured == [], "shift alone must not commit"

# Now press a real key with mods held -> commits
fk._state = {"ctrl": True, "alt": True, "x": True}
app._handle_hotkey_capture_key("x")
assert ctrl.reconfigured == ["alt+ctrl+x"], "real key with mods held should commit: %r" % ctrl.reconfigured
assert not app.in_hotkey_capture, "capture should end after commit"
print("OK  real key with mods held commits: %r" % ctrl.reconfigured)

# Real key with NO mods -> does not commit, prompts
ctrl2 = FakeController()
app2 = VoiceToTextASCIIApp(FakeConfig(), ctrl2)
app2.in_hotkey_capture = True
fk._state = {}
app2._handle_hotkey_capture_key("x")
assert ctrl2.reconfigured == [], "no-modifier key must not commit"
assert "modifier" in app2.settings_message.lower(), "should prompt to hold a modifier"
print("OK  bare key without modifier prompts instead of committing")

# esc cancels capture
app2.in_hotkey_capture = True
app2._handle_hotkey_capture_key("esc")
assert not app2.in_hotkey_capture
print("OK  esc cancels capture")

print("\nPASS: capture only commits modifier+key - hotkey persists across launches")