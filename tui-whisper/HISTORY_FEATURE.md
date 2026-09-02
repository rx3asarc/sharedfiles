# Collapsible History Log Feature

## Overview

The Voice 2E TUI now includes an enhanced collapsible history log feature, similar to Super Whisper and Whisper Flow. This provides a clean, professional way to view and manage your transcription history.

## Features

### 📋 Collapsible Entries
- **One-line preview** by default for visual clarity
- **Dropdown arrow** (▶/▼) to expand and see full transcription
- **Automatic truncation** of long text (80 characters in preview)
- **Click anywhere** on an entry to expand/collapse

### 📝 Copy Functionality
- **Copy button** (📋) on each entry
- **One-click copy** to clipboard
- **Visual feedback** with notification
- Works with the existing clipboard functionality

### ⏰ Timestamps
- Each entry shows the time it was created (HH:MM:SS format)
- Helps track when transcriptions were made

### 🎨 Visual Polish
- **Hover effects** - entries highlight when you hover over them
- **Focus styling** - keyboard navigation support
- **Newest first** - latest transcriptions appear at the top
- **Scrollable** - view up to 100 entries

## How to Use

### Viewing History
1. **Start the app**: `voice-tui` or `python -m voice_tui.main`
2. **Record audio**: Hold `Ctrl+Win` and speak
3. **View in history**: Your transcription appears at the top of the history log

### Expanding Entries
- **Click the arrow button** (▶) to expand
- **Click anywhere on the entry** to toggle expand/collapse
- **Click again** to collapse back to one line

### Copying Entries
- **Click the copy button** (📋) on any entry
- The full transcription is copied to clipboard
- A notification confirms the copy action

### Clearing History
- **Press 'C'** or select "Clear" from the shortcuts bar
- All history entries are removed
- Start fresh with a clean slate

## Technical Details

### File Structure
```
voice_tui/ui/
├── history_entry.py    # Individual collapsible entry widget
├── history_log.py      # Container for all history entries
├── main_screen.py      # Layout integration
└── styles.tcss         # Styling for history components
```

### Key Components

#### HistoryEntry Widget
- Self-contained collapsible widget
- Manages its own expand/collapse state
- Handles copy functionality independently
- Emits copy events to parent for notifications

#### HistoryLog Container
- Manages collection of HistoryEntry widgets
- Adds new entries at the top (newest first)
- Limits to 100 entries (configurable via `max_entries`)
- Provides clear functionality

### Configuration

You can customize the history log behavior by modifying `history_log.py`:

```python
class HistoryLog(VerticalScroll):
    max_entries = 100  # Change this to increase/decrease history size
```

### Styling Customization

Edit `voice_tui/ui/styles.tcss` to customize appearance:

```css
.history-entry {
    background: $surface;      /* Entry background */
    border-bottom: solid $panel; /* Separator between entries */
}

.history-entry:hover {
    background: $panel 30%;     /* Hover effect */
}

.entry-preview {
    color: $text;               /* Preview text color */
}

.entry-full-text {
    background: $panel 20%;     /* Expanded text background */
    padding: 1 2 1 5;          /* Indentation when expanded */
}
```

## Keyboard Shortcuts

- **C** - Clear all history
- **Q** - Quit application
- **S** - Open settings
- **Ctrl+Win** (hold) - Record audio

## Integration with Existing Features

### Auto-Clipboard
- Transcriptions are still automatically copied to clipboard
- History log copy button provides manual control
- Great for re-copying older transcriptions

### Auto-Type
- If auto-type is enabled, text is typed at cursor position
- History log preserves the text for later reference
- Can copy and paste manually from history

## Testing

A test application is included to demo the feature:

```bash
cd tui-whisper
python test_history.py
```

**Test controls:**
- **A** - Add random test entry
- **C** - Clear history
- **Q** - Quit

## Performance

- **Efficient rendering**: Only expanded entries show full text
- **Memory management**: Limited to 100 entries by default
- **Smooth scrolling**: Textual's optimized VerticalScroll container
- **No lag**: Even with 100 entries, the UI remains responsive

## Future Enhancements

Potential improvements for future versions:

1. **Search functionality** - Filter history by keyword
2. **Export history** - Save to file (JSON, CSV, TXT)
3. **Tags/categories** - Organize transcriptions
4. **Edit entries** - Modify transcriptions after creation
5. **Favorites** - Star important entries
6. **Persistent storage** - Save history across sessions

## Troubleshooting

### History not showing
- Make sure you've recorded at least one transcription
- Check that the app is using `app.py` (not `app_final.py`)
- Verify `main.py` imports from `from .app import VoiceToTextApp`

### Copy button not working
- Ensure `pyperclip` is installed: `pip install pyperclip`
- On Linux, install clipboard dependencies:
  - `sudo apt-get install xclip` or `xsel`
- Check clipboard permissions in system settings

### Entries not collapsing
- Click directly on the entry or the arrow button
- Check that the entry is actually expanded (▼ arrow)
- Try using a mouse if touchpad isn't responsive

## Comparison to Other Tools

### Super Whisper Style
- ✅ One-line preview with expansion
- ✅ Clean, minimal design
- ✅ Copy functionality
- ✅ Timestamps

### Whisper Flow Style
- ✅ Collapsible entries
- ✅ Visual hierarchy
- ✅ Scrollable history
- ✅ Quick access to past transcriptions

## Credits

Inspired by the history features in:
- [Super Whisper](https://superwhisper.com/) - macOS voice-to-text tool
- [Whisper Flow](https://whisperflow.com/) - Another Whisper-based transcription tool

Built using:
- [Textual](https://github.com/Textualize/textual) - Modern TUI framework
- [Rich](https://github.com/Textualize/rich) - Rich text formatting
- [pyperclip](https://github.com/asweigart/pyperclip) - Clipboard functionality
