# TUI Whisper - Unicode Conversion Session Progress

## Date
2026-03-08

## Objectives Completed ✓

### 1. ASCII to Unicode Conversion ✓
- **Changed**: Box drawing from ASCII (`+`, `-`, `|`) to Unicode (`┌`, `┐`, `└`, `┘`, `─`, `│`)
- **File**: `voice_tui/ascii_renderer.py` - `draw_box()` method
- **File**: `voice_tui/main.py` - Changed import to use `VoiceToTextASCIIApp`

### 2. Waveform Visualization - Smooth Sine Wave ✓
- **Final style**: Uses characters `_`, `⎽`, `-`, `⎺`, `⎻` for smooth sine-wave appearance
- **Pattern**: Creates flowing `-⎽__⎽-⎻⎺⎺⎻-⎽__⎽-` effect
- **File**: `voice_tui/ascii_components.py` - `ASCIIWaveformVisualizer.render()`
- **Status**: User confirmed "looks great!"
- **Evolution tried**:
  1. Unicode blocks (`▁`, `▂`, `▃`, `▄`, `▅`, `▆`, `▇`, `█`)
  2. Diagonal triangles (`◢`, `◣`) - direction was backwards
  3. Simple diagonals (`/`, `\`)
  4. **Final**: Sine-wave characters (current)

### 3. Fixed Screen Jumping ✓
- **Problem**: Screen jumping up/down 2-3 lines during rendering
- **Solution**: Changed `render_to_terminal()` to clear screen once, write sequentially
- **File**: `voice_tui/ascii_renderer.py`
- **Status**: User confirmed jumping is fixed

### 4. Fixed Flickering ✓
- **Context**: Flickering only happened when recording hotkey held down
- **Solution**: Preserved existing anti-flicker system (change detection, frame rate limiting)
- **Status**: User said "now it's basically perfect and looks much better"

### 5. Added Keyboard Input ✓
- **Q**: Quit application (no longer need Ctrl+C)
- **C**: Clear history
- **S**: Settings (placeholder)
- **File**: `voice_tui/ascii_app.py` - Added `_keyboard_listener()` thread
- **Implementation**: Works on both Windows (msvcrt) and Unix (termios)

## Current Issue - DEBUGGING ⚠️

### History Not Showing On Screen
- **Problem**: Transcriptions work, clipboard copies work, but history entries don't display
- **Evidence from debug.log**:
  ```
  Rendering 26 history lines at position (4, 23)
    Line 0: '00:19:19 "How about now when I talk? Does it flow '
    Line 1: '00:19:19 "Test 2: This is the second test entry."'
    Line 2: '00:19:19 "Test 1: History rendering works if you s'
  ```
- **Terminal Info**:
  - Size: 82x51 (columns x rows)
  - Buffer: 82x51 (matches terminal)
  - History box: starts at row 21, height 28 rows
  - Rendering position: column 4, row 23 (should be visible!)

### Debug Markers Added
- **File**: `voice_tui/ascii_app.py` - `_render_frame()` method
- **Added**: Bright test markers throughout history area:
  - `>>> HISTORY START >>> ROW X` at top
  - `*** ROW X TEST LINE ***` at multiple rows
- **Purpose**: Determine if history area renders at all

### Next Steps
1. User restarts app with test markers
2. Check if markers are visible
3. Diagnose based on results:
   - **If markers visible but no entries**: Issue with history text rendering
   - **If no markers visible**: Entire history area not rendering
   - **If markers AND entries visible**: Problem solved!

## Files Modified

### Core Changes
1. **voice_tui/main.py**
   - Line 23: Changed from `from .app import VoiceToTextApp` to `from .ascii_app import VoiceToTextASCIIApp as VoiceToTextApp`

2. **voice_tui/ascii_renderer.py**
   - `draw_box()`: Unicode box characters
   - `render_to_terminal()`: Sequential rendering to prevent jumping

3. **voice_tui/ascii_components.py**
   - `ASCIIWaveformVisualizer`: Sine-wave character visualization

4. **voice_tui/ascii_app.py**
   - Added `_keyboard_listener()` thread for Q/C/S keys
   - Added debug logging for history rendering
   - Added test markers in history area
   - Added 3 test entries on startup

## Technical Details

### Anti-Flicker System (Preserved)
- Change detection thresholds: only render when significant changes
- Render-on-demand: skip frames when nothing changed
- Frame rate: 10 FPS (reduced from 30 FPS)
- **Files**: Previously implemented in `voice_tui/ascii_app.py`

### Waveform Mapping (Current)
```python
height = int(level * 8)  # Maps 0.0-1.0 to 0-8
Characters by height:
  0: '_'   (lowest)
  1: '⎽'   (very low)
  2: '-'   (low)
  3: '⎽'   (below middle)
  4: '-'   (middle)
  5: '⎺'   (above middle)
  6: '⎻'   (high)
  7: '⎺'   (very high)
  8: '-'   (peak)
```

### Rendering Approach
- **Old**: Per-line cursor positioning `\033[row;colH` for each line
- **New**: Single clear `\033[2J` + home `\033[H`, then sequential write with newlines
- **Benefit**: Eliminates jumping, more stable

## User Feedback Quotes
- "now it's basically perfect and looks much better" (about flickering fix)
- "great! they jump. often level..." (screen was still jumping)
- "ok great" (after jumping was fixed)
- "the waveform looks great" (sine-wave visualization)
- "so the clipboard" (transcription and clipboard work, just can't see history)

## Command to Run
```bash
python -m voice_tui.main
```

## Debug Commands
```bash
# Check debug log
tail -30 debug.log

# Check terminal size info
grep -A 3 "Terminal Init" debug.log

# Check history rendering
grep "Rendering.*history" debug.log
```
