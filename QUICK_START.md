# Quick Start - Enhanced Voice-to-Text TUI

## ✅ Fixed and Ready to Run!

The stylesheet issue has been fixed. Textual doesn't support CSS `@keyframes` - it uses Python-based animations instead.

## 🚀 Run the App

### Option 1: Full App (with microphone)
```bash
voice-tui
```

### Option 2: Demo Mode (preview UI without microphone)
```bash
python demo_ui.py
```

**Demo controls:**
- Press `1` - Show Idle state
- Press `2` - Show Recording state
- Press `3` - Show Processing state
- Press `4` - Show Complete state (adds to history)
- Press `5` - Show Error state
- Press `Q` - Quit

## 🎯 Using the App

### Recording Voice
1. App starts in **Idle** state (green indicator)
2. **Hold `Ctrl+Win`** to start recording (red indicator appears)
3. Speak clearly into microphone
4. **Release `Ctrl+Win`** to stop recording
5. App processes with **Processing** state (yellow spinner)
6. **Complete** state shows result (green checkmark)
7. Text automatically copied to clipboard!
8. Returns to **Idle** after 2 seconds

### Settings
- Press `S` to open settings modal
- Change model, language, hotkey, min duration
- Click "Save" to persist to config.yaml
- Click "Cancel" or press `Esc` to close

### History
- All transcriptions logged with timestamps
- Scroll with arrow keys or mouse wheel
- Press `C` to clear history

### Keyboard Shortcuts
- `Ctrl+Win` (hold) - Record audio
- `S` - Open settings
- `C` - Clear history
- `Q` or `Ctrl+C` - Quit

## 🎨 Visual States

| State | Indicator | Description |
|-------|-----------|-------------|
| 🟢 Idle | Green ● | Ready to record |
| 🔴 Recording | Red ● | Recording with live timer + level meter |
| 🟡 Processing | Spinner | Transcribing audio |
| ✅ Complete | Green ✓ | Transcription done + copied |
| ❌ Error | Red ✗ | Error message displayed |

## 📊 Features You'll See

1. **Status Panel** - Large, clear state indicator at top
2. **Waveform** - Real-time audio visualization (during recording)
3. **Audio Level Meter** - Color-coded bar (green/yellow/red)
4. **Live Timer** - MM:SS.ms format during recording
5. **History Log** - All transcriptions with timestamps
6. **Notifications** - Toast messages for actions
7. **Settings Modal** - Interactive configuration

## 🔧 Troubleshooting

### "Error in stylesheet"
This has been fixed! The app should run now.

### No microphone detected
- Check microphone is connected and unmuted
- Check permissions: Settings > Privacy > Microphone (Windows)
- Restart the application

### Hotkey not working
- Ensure terminal window has focus
- Try alternative hotkey: `voice-tui --hotkey ctrl+alt`
- On macOS/Linux: may need `sudo voice-tui`

### Import errors
Make sure you're in the project directory:
```bash
cd C:\Users\Hp\Documents\tui-whisper
```

## 📁 Project Structure

```
tui-whisper/
├── voice_tui/
│   ├── app.py              # Main Textual application
│   ├── main.py             # Entry point
│   ├── config.py           # Configuration with save()
│   └── ui/                 # UI components
│       ├── status_panel.py    # State display
│       ├── waveform.py        # Audio visualizer
│       ├── history_log.py     # Transcription log
│       ├── settings_modal.py  # Settings dialog
│       ├── main_screen.py     # Layout composition
│       └── styles.tcss        # CSS theme (FIXED)
├── demo_ui.py              # UI preview demo
├── UI_ENHANCEMENTS.md      # Feature documentation
└── QUICK_START.md          # This file
```

## 🎉 Enjoy!

Your voice-to-text TUI now has a professional, polished interface that matches the quality of popular terminal applications like Toad, lazygit, and k9s!

Try it out:
```bash
voice-tui
```

Or preview with:
```bash
python demo_ui.py
```
