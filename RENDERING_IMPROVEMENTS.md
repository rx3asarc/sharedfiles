# Rendering Improvements - Flicker Fix

## Issues Fixed

### 1. Screen Flickering/Shaking ✅
**Problem**: Screen was jumping up and down by 10-20px every 0.2 seconds
**Cause**: Using `\n` (newlines) in render output caused terminal scrolling
**Solution**: Line-by-line cursor positioning without newlines

### 2. Waveform Not Showing ✅
**Problem**: Waveform visualization was missing during recording
**Cause**: Nothing wrong - waveform WAS rendering, just hard to see with flickering
**Solution**: Fixed with improved rendering (waveform now visible)

### 3. Performance ✅
**Problem**: Too many redraws causing visual noise
**Solution**: Reduced frame rate from 30 FPS to 10 FPS

## Changes Made

### File: `voice_tui/ascii_renderer.py`

**Before** (caused flickering):
```python
def render_to_terminal(self):
    sys.stdout.write('\033[H')  # Home cursor

    # This causes scrolling!
    output = []
    for row in self.buffer:
        output.append(''.join(row))
    sys.stdout.write('\n'.join(output))  # Newlines cause scroll
```

**After** (flicker-free):
```python
def render_to_terminal(self):
    # Position cursor for each line individually
    output_parts = []
    for row_idx, row in enumerate(self.buffer):
        # ANSI cursor position: \033[row;colH
        output_parts.append(f'\033[{row_idx + 1};1H')
        output_parts.append(''.join(row))

    # Write all at once (no newlines = no scrolling)
    sys.stdout.write(''.join(output_parts))
```

### File: `voice_tui/ascii_app.py`

#### Change 1: Alternate Screen Buffer
**Before**:
```python
def _init_terminal(self):
    sys.stdout.write("\033[?25l")  # Hide cursor
    sys.stdout.write("\033[2J")    # Clear screen
    sys.stdout.write("\033[H")     # Home cursor
```

**After**:
```python
def _init_terminal(self):
    sys.stdout.write("\033[?1049h")  # Switch to alternate screen
    sys.stdout.write("\033[?25l")    # Hide cursor
    sys.stdout.write("\033[2J")      # Clear screen
    sys.stdout.write("\033[H")       # Home cursor
```

**Benefits**:
- Alternate screen buffer prevents scrollback pollution
- Original terminal content preserved
- Clean return to normal terminal on exit

#### Change 2: Reduced Frame Rate
**Before**:
```python
self.target_fps = 30  # Too fast for text UI
```

**After**:
```python
self.target_fps = 10  # Sufficient for text updates
```

**Benefits**:
- Less CPU usage
- Fewer redraws
- Still smooth enough for text UI

## Technical Details

### ANSI Escape Sequences Used

| Code | Function | Purpose |
|------|----------|---------|
| `\033[?1049h` | Enable alternate screen | Switch to clean screen buffer |
| `\033[?1049l` | Disable alternate screen | Return to main buffer |
| `\033[?25l` | Hide cursor | Cleaner rendering |
| `\033[?25h` | Show cursor | Restore on exit |
| `\033[2J` | Clear screen | Initial clear |
| `\033[{row};{col}H` | Position cursor | Per-line positioning |

### Rendering Flow

```
1. Initialize terminal
   ├─ Switch to alternate screen buffer
   ├─ Hide cursor
   └─ Clear screen

2. Main loop (10 FPS)
   ├─ Process updates from queue
   ├─ Clear internal buffer
   ├─ Render all UI sections to buffer
   ├─ Output buffer line-by-line with cursor positioning
   └─ Sleep for frame time (100ms)

3. Cleanup
   ├─ Show cursor
   ├─ Clear screen
   └─ Return to main screen buffer
```

### Line-by-Line Positioning Algorithm

```python
# For each line in the buffer:
for row_idx in range(height):
    # Position cursor at start of line (1-based indexing)
    output += f'\033[{row_idx + 1};1H'

    # Write line content (no newline!)
    output += ''.join(buffer[row_idx])

# Write all lines at once
sys.stdout.write(output)
sys.stdout.flush()
```

**Why This Works**:
- No newlines = no scrolling
- Absolute positioning = no relative movement
- Batch write = atomic update (less flicker)

## Performance Impact

### Before
- **FPS**: 30
- **Frame time**: 33ms
- **Renders per second**: 30
- **Flickering**: Yes (newlines cause scroll)

### After
- **FPS**: 10
- **Frame time**: 100ms
- **Renders per second**: 10
- **Flickering**: No (absolute positioning)
- **CPU savings**: ~66% fewer renders

## Testing

### Visual Test
```bash
python test_ascii_render_all.py
```

Should see:
- ✅ Steady, stable rendering
- ✅ No screen shake
- ✅ Waveform visible during recording
- ✅ Smooth transitions

### Live Recording Test
```bash
python -m voice_tui.main
```

Then:
1. Hold Ctrl+Win to start recording
2. Observe:
   - ✅ Waveform animates smoothly
   - ✅ Timer updates without flicker
   - ✅ Level bar changes smoothly
   - ✅ No screen jumping

## Waveform Visualization

Now properly visible during recording:

```
+------------------------------ Waveform Visualization ------------------------------+
|            #         #         #         #         #         #         #         # |
|      ===+++#   ===+++#   ===+++#   ===+++#   ===+++#   ===+++#   ===+++#   ===+++# |
|   ---===+++#---===+++#---===+++#---===+++#---===+++#---===+++#---===+++#---===+++# |
+------------------------------------------------------------------------------------+
```

Character mapping:
- ` ` (space) = Silence
- `-` = Low level
- `=` = Medium level
- `+` = High level
- `#` = Peak level

## Known Limitations

### Terminal Compatibility
- Requires ANSI escape code support
- Tested on: Windows Terminal, PowerShell, CMD, Git Bash, WSL
- May not work on very old terminals

### Refresh Rate
- 10 FPS = 100ms latency
- Good enough for text UI
- Can increase to 20 FPS if needed (change `target_fps`)

## Future Improvements

Potential optimizations:
1. **Dirty rectangle tracking** - Only redraw changed regions
2. **Double buffering** - Compare old vs new buffer, only update diffs
3. **Compression** - Send only changed lines
4. **Adaptive FPS** - Higher FPS during recording, lower when idle

## Summary

The rendering system is now:
- ✅ **Flicker-free**: No screen shake or jumping
- ✅ **Stable**: Line-by-line positioning prevents scrolling
- ✅ **Efficient**: 10 FPS reduces CPU usage
- ✅ **Clean**: Alternate screen buffer isolates UI
- ✅ **Complete**: Waveform and all sections render correctly

**The UI is now production-ready with smooth, stable rendering!**
