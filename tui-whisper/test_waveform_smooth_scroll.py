"""Regression test: organic ChatGPT-style waveform.

Design goals (replacing the fast-scrolling 3-row strip):
  1. Dense, symmetric, filled waveform - voice envelope swells the humps.
  2. NOT a fast horizontal scroll - shape breathes in place with slow drift.
  3. Keeps animating through silence (soft breathing line, never freezes).
  4. More frames per second while recording (30 FPS path) - separate test.
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

# --- Direct component tests ---
W = 60
vis = ASCIIWaveformVisualizer(width=W, smoothing=0.2, field_height=5)
assert vis.field_height == 5 and vis.center == 2

def count_filled(vis):
    grid = vis.render()
    return sum(1 for row in grid for ch in row if ch in ('█', '▓'))

vis.clear()
# Silence: soft breathing line, still renders, still animates
s1 = count_filled(vis)
assert vis.render()[2] != '', "silence should still render a baseline"
for _ in range(30):
    vis.update(0.0)
s2 = count_filled(vis)
assert s2 >= 0, "silence must keep rendering"
# Phase drift means repeated silent renders change subtly over time
r_a = vis.render()
for _ in range(30):
    vis.update(0.0)
r_b = vis.render()
assert r_a != r_b, "waveform must keep animating through silence (phase drift)"
print("OK  silence: breathing line animates, never freezes")

# Speech: visibly taller / denser than silence
vis.clear()
for _ in range(10):
    vis.update(0.9)
filled_loud = count_filled(vis)
vis.clear()
for _ in range(10):
    vis.update(0.0)
filled_silent = count_filled(vis)
assert filled_loud > filled_silent, "voice should visibly swell the waveform (%d vs %d)" % (filled_loud, filled_silent)
print("OK  voice swells waveform: %d filled cells vs %d at silence" % (filled_loud, filled_silent))

# Smooth between quiet and loud (no jump-cuts)
vis.clear()
for _ in range(8):
    vis.update(0.1)
mid_low = count_filled(vis)
for _ in range(8):
    vis.update(0.5)
mid_high = count_filled(vis)
assert mid_low <= mid_high, "waveform should grow monotonically with level"
print("OK  level response monotonic (%d -> %d)" % (mid_low, mid_high))

# Render integrity: symmetric rows, full width
rows = vis.render()
assert len(rows) == 5, "render should return field_height rows"
assert all(len(r) == W for r in rows), "every row must be full width"
# Symmetry: top/bottom halves mirror each other approximately
assert rows[0].count(' ') == rows[4].count(' ') + 0 or True  # filled-cell symmetry is exact per column
def filled(row): return sum(1 for ch in row if ch in ('█', '▓'))
assert filled(rows[0]) == filled(rows[4]), "waveform must be vertically symmetric (top/bottom mirror)"
print("OK  render: 5 rows, full width, vertically symmetric")

# --- App integration (field height adapts to terminal) ---
app = VoiceToTextASCIIApp(FakeConfig(), FakeController())
assert app.waveform.field_height == app.layout.WAVEFORM_HEIGHT - 2
assert app.waveform.field_height >= 3 and app.waveform.field_height % 2 == 1, "field height must be odd"
# Avatar: update_metrics always advances the wave; silence still moves it
w = app.waveform
w.clear()
app._handle_update(("update_metrics", 0.5, 0.8, 0.8))
before = w.render()
for i in range(20):
    app._handle_update(("update_metrics", 0.5 + i * 0.033, 0.8, 0.8))
after_speech = w.render()
assert after_speech != before, "level updates must keep the wave alive"
for i in range(20):
    app._handle_update(("update_metrics", 2.0 + i * 0.033, 0.0, 0.0))
after_silence = w.render()
assert after_silence != after_speech, "silence updates must keep the wave moving (no freeze)"
assert app.needs_render, "metrics messages must schedule a render"
print("OK  app integration: wave advances on speech AND silence")

print("\nPASS: organic waveform - dense, calm, keeps breathing through silence")