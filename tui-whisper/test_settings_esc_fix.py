"""Regression test: after changing hotkey in settings, esc must exit settings.

Simulates the keyboard.hook event flow end-to-end with a fake keyboard module.
The fake controller mimics main.py's reconfigure_hotkey: it calls
keyboard.unhook_all() (which kills the UI hook), then re-registers via
app.rehook_ui_keys() -- exactly the bug path that left the TUI deaf.
"""
import sys
import types

# --- Fake keyboard module ---
fake_keyboard = types.ModuleType("keyboard")
fake_keyboard._hooks = []
fake_keyboard._pressed = {}  # modifier -> bool

def hook(cb):
    fake_keyboard._hooks.append(cb)
    return cb

def unhook_all():
    fake_keyboard._hooks.clear()

def is_pressed(mod):
    return fake_keyboard._pressed.get(mod, False)

fake_keyboard.hook = hook
fake_keyboard.unhook_all = unhook_all
fake_keyboard.is_pressed = is_pressed
sys.modules["keyboard"] = fake_keyboard

from voice_tui.ascii_app import VoiceToTextASCIIApp

# --- Fake config / controller ---
class FakeConfig:
    def __init__(self):
        self.hotkey = "ctrl+space"

ctrl_reconfigure_calls = []

class FakeController:
    def __init__(self):
        self.config = FakeConfig()
        self.app = None  # set below

    def reconfigure_hotkey(self, new_hotkey):
        # Mirrors real main.py behavior: unwire everything, then rehook.
        fake_keyboard.unhook_all()
        ctrl_reconfigure_calls.append(new_hotkey)
        self.config.hotkey = new_hotkey
        if self.app:
            self.app.rehook_ui_keys()  # the fix: UI hook comes back

ctrl = FakeController()
app = VoiceToTextASCIIApp(FakeConfig(), ctrl)
ctrl.app = app

# Register the UI hook the same way _keyboard_listener() does
# (running=False so the listener thread body returns right after hooking).
app._keyboard_listener()
assert len(fake_keyboard._hooks) == 1, "expected 1 UI hook, got %d" % len(fake_keyboard._hooks)

def key_press(name):
    """Simulate a key down event through the UI hook."""
    class Ev:
        pass
    ev = Ev()
    ev.event_type = 'down'
    ev.name = name
    for cb in list(fake_keyboard._hooks):
        cb(ev)

# 1. Open settings
key_press('s')
assert app.settings_mode, "s should open settings"

# 2. Navigate down to Hotkey (cursor 0=Model, 1=Language, 2=Hotkey)
key_press('s')
key_press('s')
assert app.settings_cursor == 2, "cursor should be on Hotkey, got %d" % app.settings_cursor

# 3. Enter hotkey capture
key_press('e')
assert app.in_hotkey_capture, "e should start hotkey capture"

# 4. Press new combo ctrl+alt+x
fake_keyboard._pressed = {'ctrl': True, 'alt': True}
key_press('x')
assert not app.in_hotkey_capture, "capture should end after combo"
assert ctrl_reconfigure_calls == ['alt+ctrl+x'], ctrl_reconfigure_calls
assert app.settings_mode, "still in settings (navigation), should not have exited"
assert len(fake_keyboard._hooks) >= 1, "UI hook must be re-registered after reconfigure"

# 5. THE BUG: esc must exit settings now
key_press('esc')
assert not app.settings_mode, "esc should exit settings after hotkey change"

# 6. After exiting, the UI still responds (q quits)
key_press('q')
assert not app.running, "q should quit the app"

print("PASS: settings usable after hotkey change; esc exits; q quits")