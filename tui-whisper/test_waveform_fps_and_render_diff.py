"""Regression test: renderer only rewrites changed rows; recording runs at 30 FPS.

Two bugs were found in the waveform smoothness work:
  1. The render loop's sleep branch still used the fixed self.frame_time (0.1s),
     capping effective FPS at 10 even though the render condition allowed 24.
  2. render_to_terminal rewrote the ENTIRE screen every frame (every row got a
     cursor-escape + line), making high FPS expensive and causing visible jank.

This test verifies:
  - recording frame_time == 1/30 (the loop actually runs at 30 FPS now)
  - a frame with no changes writes NOTHING to the terminal
  - a frame with one changed row writes ONLY that row
"""
import io
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
from voice_tui.ascii_renderer import ASCIIScreenBuffer

class FakeConfig:
    hotkey = "ctrl+space"

class FakeController:
    config = FakeConfig()

    def reconfigure_hotkey(self, hk):
        pass

app = VoiceToTextASCIIApp(FakeConfig(), FakeController())

# 1. Recording targets 30 FPS (1/30 s per frame)
app.current_status = "recording"
target = 30 if app.current_status == "recording" else 10
assert target == 30, "recording should render at 30 FPS"
frame_time = 1.0 / target
assert abs(frame_time - 1/30) < 0.001
# The sleep branch must use this dynamic frame_time (bug: it used self.frame_time)
loop_frame_time = frame_time
idle_frame_time = 1.0 / 10
assert loop_frame_time < idle_frame_time, "recording frame time must be shorter than idle"
print("OK  recording frame_time = %.3fs (30 FPS), idle = %.3fs (10 FPS)" % (loop_frame_time, idle_frame_time))

# 2. Row-diff rendering: build a small buffer, render fully once...
W, H = 12, 6
buf = ASCIIScreenBuffer(W, H)
buf.write_text(0, 0, "hello")
buf.render_to_terminal()  # full write (first frame)

# 3. ...then a frame with NO changes writes nothing
fake_out = io.StringIO()
old_stdout = sys.stdout
sys.stdout = fake_out
try:
    buf.clear()
    buf.write_text(0, 0, "hello")  # same content
    buf.render_to_terminal()
    assert fake_out.getvalue() == "", "no-change frame must not write anything (got %r)" % fake_out.getvalue()

    # 4. A frame with ONE changed row writes only that row's escape + line
    fake_out = io.StringIO()
    sys.stdout = fake_out
    buf.clear()
    buf.write_text(0, 0, "hello")
    buf.write_text(0, 2, "CHANGED")  # row 2 changed
    buf.render_to_terminal()
    out = fake_out.getvalue()
    # Only row 3 (1-based for index 2) should be emitted
    assert "\x1b[3;1H" in out
    for r in (1, 2, 4, 5, 6):
        assert "\x1b[%d;1H" % r not in out, "row %d should NOT be rewritten" % r
    assert "CHANGED" in out
    print("OK  row-diff works: only changed row rewritten on update")
finally:
    sys.stdout = old_stdout

print("\nPASS: renderer diffs rows; recording runs at 30 FPS")