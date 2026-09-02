r"""Regression test: natural transcription formatting + wrapped history display.

The old local formatter split sentences on `([.!?]\s+)` KEEPING the delimiters
as separate segments, so output looked like:

    Sentence one
    <blank>
    .
    <blank>
    Sentence two

i.e. "line break period line break" between every sentence. It also joined
every part with '\\n\\n' so even correct segments were forced onto separate
lines. The history display additionally truncated long entries to one line.

Design goals (matching natural dictation/chat voice UX):
  1. Plain prose flows as ONE paragraph - sentences joined with spaces.
  2. No stray "." on its own line, no per-sentence line breaks.
  3. Genuine structures still detected: category lists (2+ "X: a, b") and
     explicit numbered steps ("1. ... 2. ...").
  4. Decimals like "3.5" never mangled.
  5. History display wraps long entries over multiple lines, not "...".
"""
import sys
import types
from datetime import datetime

# --- Hermetic stubs ---
fake_whisper = types.ModuleType("faster_whisper")
fake_whisper.WhisperModel = object
sys.modules["faster_whisper"] = fake_whisper

import numpy as np  # real numpy is installed on this box

from voice_tui.transcriber import WhisperTranscriber
from voice_tui.ascii_components import ASCIIHistoryLog

tr = WhisperTranscriber.__new__(WhisperTranscriber)


def fmt(s):
    return tr._format_transcription(s)


# --- 1. Plain prose: single flowing paragraph, no newlines, no stray periods ---
out = fmt("by the way this is me just going to be talking right now and i want you "
          "to notice the output. you are gonna see this by seeing this message. "
          "that is what we need to fix. it should be much more natural.")
assert "\n" not in out, "plain prose must not contain line breaks: %r" % out
assert ".\n" not in out and "\n." not in out
assert out.startswith("By the way"), out
assert out.count(".") == 4, "exactly one period per sentence, nothing stray"
print("OK  1. plain prose flows as one paragraph")

# --- 2. Dictation-style multi-sentence ---
out = fmt("hello world. this is a test. it flows naturally.")
assert out == "Hello world. This is a test. It flows naturally.", out
print("OK  2. dictation-style text clean, single paragraph")

# --- 3. Category list still structured ---
out = fmt("i am going shopping. fruits: bananas, apples. vegetables: carrots, celery.")
assert "**Fruits:**" in out and "**Vegetables:**" in out
assert "• Bananas" in out and "• Carrots" in out
print("OK  3. category lists still get headers + bullets")

# --- 4. Explicit numbered steps still structured ---
out = fmt("1. open the app. 2. go to settings. 3. press the hotkey.")
assert out == "1. Open the app.\n2. Go to settings.\n3. Press the hotkey.", out
print("OK  4. explicit numbered steps become a list")

# --- 5. Decimals preserved ---
out = fmt("the measurement is 3.5 and it is good. another sentence follows.")
assert "3.5" in out and "3. 5" not in out, out
print("OK  5. decimals like 3.5 preserved")

# --- 6. Single sentence ---
assert fmt("just one sentence.") == "Just one sentence."
print("OK  6. single sentence handled")

# --- 7. History wraps long entries instead of truncating ---
h = ASCIIHistoryLog(max_visible=20, max_entries=100)
long_text = ("By the way this is me just going to be talking right now and i want "
             "you to notice the output. you are gonna see this by seeing this "
             "message. that is what we need to fix. it should be much more natural.")
h.add_entry(datetime.now(), long_text)
h.add_entry(datetime.now(), "Short entry here.")

lines = h.render(height=12, max_width=60)
assert lines[0].startswith('2') and '"Short entry here."' in lines[0]
# The first line of the long entry carries the timestamp; continuations are indented
first_long = [i for i, l in enumerate(lines) if "By the way" in l][0]
assert lines[first_long].startswith('2'), "long entry line should still carry timestamp"
assert "By the way" in lines[first_long]
assert "more natural" in "\n".join(lines), "full text must be visible across wrapped lines"
assert "..." not in "\n".join(lines), "no ellipsis truncation anymore"
print("OK  7. history wraps long transcriptions across lines")

print("\nPASS: natural flowing transcription + wrapped display")