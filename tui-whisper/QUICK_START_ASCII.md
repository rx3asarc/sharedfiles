# Quick Start Guide - ASCII UI

## Overview

The application uses a pure ASCII rendering system that **automatically adapts to any terminal size**.

### Key Features
- ✅ **Dynamic sizing**: Adapts to terminals from 60×25 to 200×100+
- ✅ **Auto-resize**: Detects and responds to terminal resizing
- ✅ **Pure ASCII**: Only characters 32-126 (maximum compatibility)
- ✅ **High performance**: 30 FPS with minimal CPU usage

## Running the Application

The application now uses the new ASCII rendering system by default.

### Basic Usage

```bash
# Run with default settings (auto-detects terminal size)
python -m voice_tui.main

# Or if installed
voice-tui
```

### Testing the UI

```bash
# View all UI states (static rendering test)
python test_ascii_render_all.py

# Test dynamic sizing at different terminal sizes
python test_dynamic_sizing.py

# Interactive test (requires terminal with input)
python test_ascii_render.py
```

### Verification

```bash
# Verify ASCII-only characters
python verify_ascii_only.py

# Test dynamic sizing
python test_dynamic_sizing.py

# Test imports
python -c "from voice_tui.ascii_app import VoiceToTextASCIIApp; print('OK')"
```

## Terminal Size Requirements

### Supported Sizes
- **Minimum**: 60 columns × 25 rows (basic functionality)
- **Recommended**: 90 columns × 40 rows (original design, optimal)
- **Comfortable**: 100 columns × 45 rows (more history visible)
- **Large**: 120+ columns × 50+ rows (maximum visibility)

### Dynamic Behavior
The UI automatically:
- Detects your terminal size on startup
- Adapts all panels and boxes to fit
- Expands history section to use available space
- Detects resize events and re-layouts in real-time

### Resize Your Terminal
You can resize your terminal window at any time:
1. The app detects size changes every second
2. Layout automatically recalculates
3. Screen refreshes with new dimensions
4. No restart needed!

## UI Layout (Example: 90×40)

```
Row  0: Voice-to-Text TUI | Status: [Current State]
Row  1: -----------------------------------------------------------------
Row  3: +----------------------- Status Panel -----------------------+
     4: |  [State-specific content]                                   |
     5: |  * READY TO RECORD / RECORDING / TRANSCRIBING...           |
     6: |  [Details]                                                  |
     7: |  [Progress bars, timers, messages]                         |
     8: |                                                             |
     9: +-------------------------------------------------------------+
Row 11: +-------------------- Waveform Visualization -----------------+
    12: |  [ASCII waveform - only visible during recording]          |
    13: |  ::--==++##++==--::--==++##++==--::                        |
    14: |                                                             |
    15: +-------------------------------------------------------------+
Row 17: Recording: 00:03.45 | Level: [####.....] 45% | Peak: 87%
Row 19: Recent Transcriptions:
Row 20: -----------------------------------------------------------------
Row 21: +-------------------------------------------------------------+
    22: | 14:32:15 "This is a transcription..."                       |
    23: | 14:31:42 "Another transcription..."                         |
     …: | [More entries...]                                           |
    34: +-------------------------------------------------------------+
Row 36: -----------------------------------------------------------------
Row 37: [Ctrl+Shift+Z] Record | [Q] Quit | [S] Settings | [C] Clear

Total: 90 columns × 40 rows
```

## Character Set

All UI elements use ASCII characters (32-126):

- **Boxes**: `+` (corners), `-` (horizontal), `|` (vertical)
- **Waveform**: ` .:-=+*#` (8 levels from silence to peak)
- **Progress**: `[####......]` (filled=`#`, empty=`.`)
- **Indicators**: `*` (bullet), `X` (error)

## State Flow

```
IDLE
  ↓ [Press Ctrl+Shift+Z]
RECORDING (shows waveform + metrics)
  ↓ [Release Ctrl+Shift+Z]
PROCESSING (shows "Transcribing...")
  ↓ [Transcription complete]
COMPLETE (shows result + adds to history)
  ↓ [Auto-transition after 2s]
IDLE
```

## Features

- **Real-time recording metrics**: Timer, audio level, peak level
- **Live waveform visualization**: ASCII mountain showing audio amplitude
- **History log**: Last 100 transcriptions with timestamps
- **Thread-safe updates**: Background transcription doesn't block UI
- **Efficient rendering**: 30 FPS with dirty tracking

## Troubleshooting

### UI not rendering correctly
- Ensure terminal is at least 90 columns wide
- Try resizing terminal window
- Check terminal supports ANSI escape codes

### Hotkey not working
- Run with administrator/root privileges
- Check `debug.log` for hotkey registration messages
- Verify keyboard library is installed

### Import errors
```bash
# Verify installation
pip install -r requirements.txt

# Check imports
python -c "from voice_tui.ascii_app import VoiceToTextASCIIApp"
```

## Reverting to Textual UI

If you need to use the old Textual interface:

1. Edit `voice_tui/main.py` line 23:
   ```python
   # Change this:
   from .ascii_app import VoiceToTextASCIIApp as VoiceToTextApp

   # Back to this:
   from .app import VoiceToTextApp
   ```

2. Restart the application

## Performance Notes

- **FPS**: 30 frames per second (default)
- **Frame time**: ~33ms per frame
- **CPU usage**: Minimal when idle, moderate during recording
- **Memory**: Low footprint (~20MB)

## Known Limitations

- Fixed 90-column width (terminal resize not handled)
- No color support (pure ASCII)
- No scrolling in history (shows last N entries)
- Keyboard commands (Q, S, C) not yet implemented in ASCII version

## Development

### File Structure
```
voice_tui/
├── ascii_app.py        # Main ASCII application
├── ascii_components.py # UI component renderers
├── ascii_layout.py     # Layout specifications
├── ascii_renderer.py   # Core rendering engine
└── main.py            # Entry point (uses ASCII app)

test_ascii_render.py          # Interactive tests
test_ascii_render_all.py      # Automated tests
verify_ascii_only.py          # Character verification
```

### Adding New Features

To modify the UI:
1. Update layout in `ascii_layout.py` if needed
2. Modify component rendering in `ascii_components.py`
3. Update main render loop in `ascii_app.py`
4. Test with `test_ascii_render_all.py`

## Support

For issues or questions:
- Check [[ASCII_IMPLEMENTATION]] for technical details
- Review [[IMPLEMENTATION_SUMMARY]] for overview
- Examine test scripts for examples
