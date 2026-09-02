"""Regression test: waveform must keep scrolling with more frames.

1. EVERY update_metrics message advances the waveform buffer (was dropped by
   a 2% level-change / 0.1s duration threshold, causing choppy ~10 Hz motion).
2. When audio goes silent (level -> 0), the wave KEEPS scrolling as a flat
   line instead of freezing in place.
3. needs_render is set on every message so the render loop (24 FPS while
   recording) always draws fresh waveform data.
"""
import sys
import types

# --- Fake keyboard module (ascii_app imports it) ---
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

from voice_tui.ascii_app import VoiceToTextASCIIApp
from voice_tui.ascii_components import ASCIIWaveformVisualizer

class FakeConfig:
    hotkey = "ctrl+space"

class FakeController:
    config = FakeConfig()

    def reconfigure_hotkey(self, hk):
        pass

app = VoiceToTextASCIIApp(FakeConfig(), FakeController())

W = app.layout.PANEL_WIDTH - 4
assert app.waveform.width == W

# 1. Speech: send a burst of varying levels -> buffer advances every message
app.waveform.clear()
for i in range(W):
    level = 0.3 + 0.4 * (i % 5) / 4.0  # varying 0.3..0.7
    app._handle_update(("update_metrics", i * 0.033, level, level))
# After W messages the buffer should be fully populated (no leading zeros)
assert all(v > 0.0 for v in app.waveform.buffer), "buffer should fill with speech levels"
assert app.needs_render, "every metrics message should schedule a render"
print("OK  speech: buffer advanced & filled (%.0f samples at ~30 Hz)" % W)

# 2. Record a snapshot of the buffer, then SILENCE: level 0 for W/2 messages
snapshot = list(app.waveform.buffer)
for i in range(W // 2):
    app._handle_update(("update_metrics", (W + i) * 0.033, 0.0, 0.0))
scrolled = app.waveform.buffer
# The buffer must have moved: newest entries should now be ~0 (silence scrolled
# in via EMA decay; visually flat well before 8*level < 1).
assert abs(scrolled[-1]) < 1e-3 and abs(scrolled[-10]) < 1e-3, \
    "silence should scroll flat zeros (got %r)" % scrolled[-3:]
assert scrolled != snapshot, "buffer must keep scrolling through silence"
assert len(scrolled) == W
print("OK  silence: waveform keeps scrolling (flat line), no freeze")

# 3. And when speech returns, the wave animates again immediately
app._handle_update(("update_metrics", 1.0, 0.6, 0.6))
app._handle_update(("update_metrics", 1.033, 0.5, 0.5))
assert app.waveform.buffer[-1] > 0.0, "waveform should respond to resumed speech"
print("OK  speech resumes after silence")

# 4. Visualizer renders without error at all levels
lines = app.waveform.render()
assert len(lines) == 3 and all(len(l) == W for l in lines), "render should return 3 full-width rows"
print("OK  render produces 3 full-width rows")

print("\nPASS: waveform is smooth (30 Hz samples) and keeps scrolling through silence")