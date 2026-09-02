# ASCII UI Implementation

## Overview

The TUI has been successfully redesigned from Textual-based widgets to a pure ASCII rendering system. The new implementation uses only basic ASCII characters (32-126) for all UI elements.

## New Files Created

### 1. `voice_tui/ascii_renderer.py`
Core rendering engine providing:
- `ASCIIScreenBuffer` - 2D character buffer for terminal rendering
- Box drawing using `+`, `-`, `|` characters
- Text positioning and centering
- ANSI escape code terminal output
- Dirty tracking for efficient updates

### 2. `voice_tui/ascii_layout.py`
Layout specification defining:
- Fixed 90x40 character grid
- Exact row/column positions for all UI sections
- Panel margins and widths
- All coordinates as constants

### 3. `voice_tui/ascii_components.py`
Rendering components:
- `ASCIIStatusPanel` - Status display (idle, recording, processing, complete, error)
- `ASCIIWaveformVisualizer` - Audio waveform using ASCII mountain (`.:-=+*#`)
- `ASCIIMetricsRow` - Recording metrics (timer, level, peak)
- `ASCIIHistoryLog` - Transcription history with timestamps

### 4. `voice_tui/ascii_app.py`
Main application class:
- `VoiceToTextASCIIApp` - Replacement for Textual `VoiceToTextApp`
- Maintains same interface for controller compatibility
- Custom render loop (30 FPS default)
- Thread-safe update queue
- All controller methods preserved

### 5. `test_ascii_render.py` & `test_ascii_render_all.py`
Test scripts for verifying static frame rendering.

## Modified Files

### `voice_tui/main.py`
**Single line change:**
```python
# OLD:
from .app import VoiceToTextApp

# NEW:
from .ascii_app import VoiceToTextASCIIApp as VoiceToTextApp
```

## ASCII Character Set

All UI elements use only ASCII characters (32-126):

### Box Drawing
- Corners: `+`
- Horizontal: `-`
- Vertical: `|`

### Waveform Visualization (8 levels)
- ` ` (space) - Silence
- `.` - Very quiet
- `:` - Quiet
- `-` - Moderate
- `=` - Normal
- `+` - Loud
- `*` - Very loud
- `#` - Peak

### Status Indicators
- `*` - Bullet/indicator
- `X` - Error marker
- `[####....]` - Progress bars

## Layout Structure

```
Row  0: Header (centered)
Row  1: Header separator (dashes)
Row  3-9: Status Panel (7 rows, includes border)
Row 11-15: Waveform (5 rows, visible only when recording)
Row 17: Metrics row (visible only when recording)
Row 19: History title
Row 20: History separator
Row 21-34: History box (14 rows, includes border)
Row 36: Footer separator
Row 37: Footer (centered)

Width: 90 characters
Height: 40 rows (38 used)
Panel margins: 2 characters from edges
```

## State Display

### Idle State
```
+----------------------------------- Status Panel -----------------------------------+
|                                                                                    |
|  * READY TO RECORD                                                                 |
|                                                                                    |
|  Hold [Ctrl+Win] to record                                                         |
|                                                                                    |
+------------------------------------------------------------------------------------+
```

### Recording State
```
+----------------------------------- Status Panel -----------------------------------+
|                                                                                    |
|  * RECORDING                                                                       |
|                                                                                    |
|  Recording: 00:03.45                                                               |
|  Level: [#########...........] 45%                                                 |
+------------------------------------------------------------------------------------+

+------------------------------ Waveform Visualization ------------------------------+
|            #         #         #         #         #         #         #         # |
|       ===++#    ===++#    ===++#    ===++#    ===++#    ===++#    ===++#    ===++# |
|   ::--===++#::--===++#::--===++#::--===++#::--===++#::--===++#::--===++#::--===++# |
+------------------------------------------------------------------------------------+

  Recording: 00:03.45 | Level: [######.........] 45% | Peak: 87%
```

### Processing State
```
+----------------------------------- Status Panel -----------------------------------+
|                                                                                    |
|  TRANSCRIBING...                                                                   |
|                                                                                    |
|  Please wait                                                                       |
|                                                                                    |
+------------------------------------------------------------------------------------+
```

### Complete State
```
+----------------------------------- Status Panel -----------------------------------+
|                                                                                    |
|  * TRANSCRIPTION COMPLETE                                                          |
|                                                                                    |
|  This is a preview of the transcribed text...                                      |
|                                                                                    |
+------------------------------------------------------------------------------------+

Recent Transcriptions:
------------------------------------------------------------------------------------------
+------------------------------------------------------------------------------------+
| 19:13:26 "This is a very long transcription that will be truncated to fit the..."  |
| 19:13:26 "Short text."                                                             |
| 19:13:26 "Another entry showing multiple transcriptions."                          |
+------------------------------------------------------------------------------------+
```

### Error State
```
+----------------------------------- Status Panel -----------------------------------+
|                                                                                    |
|  X ERROR                                                                           |
|                                                                                    |
|  Recording failed: No microphone detected                                          |
|                                                                                    |
+------------------------------------------------------------------------------------+
```

## Controller Interface Compatibility

All controller methods remain unchanged:
- `set_status(status, message="")`
- `update_recording_metrics(duration, audio_level, peak_level)`
- `set_transcription(text, copied=False, auto_typed=False)`
- `update_transcription(formatted_text)`
- `show_error(error_message)`
- `call_from_thread(method, *args)`

## Thread Safety

The new implementation uses a thread-safe `queue.Queue` for cross-thread updates:
- Controller threads push updates to queue
- Main render loop processes queue each frame
- No shared mutable state between threads

## Performance

- Target: 30 FPS (configurable)
- Frame time: ~33ms per frame
- Dirty tracking for efficient rendering
- Minimal CPU usage when idle

## Testing

Run static rendering tests:
```bash
python test_ascii_render_all.py
```

This displays all UI states (idle, recording, processing, complete, error) with sample data.

## Rollback

To revert to Textual implementation, change line 23 in `voice_tui/main.py`:
```python
# Revert to:
from .app import VoiceToTextApp
```

The old Textual code in `voice_tui/app.py` and `voice_tui/ui/*.py` remains untouched as a fallback.

## Future Enhancements

Potential improvements:
1. Add keyboard input handling for commands (Q, S, C)
2. Implement scrolling in history log
3. Add color using ANSI color codes (optional)
4. Optimize dirty-rect tracking for large buffers
5. Add terminal size detection and adaptation
