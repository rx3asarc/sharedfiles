# Quick Start: Collapsible History Feature

## Visual Guide

### What It Looks Like

#### Collapsed View (Default)
```
┌─ Recent Transcriptions: ─────────────────────────────┐
│                                                      │
│ ▶ 14:23:15  This is a short test transcription. 📋 │
│ ▶ 14:22:08  This is a much longer transcription ... 📋│
│ ▶ 14:21:45  Quick note: Buy milk and eggs from ... 📋│
│ ▶ 14:20:32  Meeting notes: Discussed the new fe ... 📋│
│ ▶ 14:19:18  Reminder: Call doctor tomorrow at 2 ... 📋│
│                                                      │
└──────────────────────────────────────────────────────┘
```

#### Expanded View (After Clicking)
```
┌─ Recent Transcriptions: ─────────────────────────────┐
│                                                      │
│ ▼ 14:22:08  This is a much longer transcription ... 📋│
│     This is a much longer transcription that will   │
│     be truncated in the preview. It contains        │
│     multiple sentences and demonstrates how the     │
│     collapsible history entries work when the       │
│     text is very long. You can click the arrow      │
│     button to expand and see the full text.         │
│                                                      │
│ ▶ 14:21:45  Quick note: Buy milk and eggs from ... 📋│
│ ▶ 14:20:32  Meeting notes: Discussed the new fe ... 📋│
│                                                      │
└──────────────────────────────────────────────────────┘
```

## 3-Step Usage

### Step 1: Record
Hold **Ctrl+Shift+Z** and speak your text.

### Step 2: View
Your transcription appears at the top of the history log.

### Step 3: Interact
- **Click entry** → Expand/collapse
- **Click 📋** → Copy to clipboard
- **Press C** → Clear all history

## Quick Demo

### Try It Now!
```bash
cd tui-whisper
python test_history.py
```

### Controls
- **A** - Add test entry
- **C** - Clear history
- **Q** - Quit
- **Click** - Expand/collapse entries

## Features at a Glance

| Feature | Description |
|---------|-------------|
| 🔽 Collapsible | Click to expand/collapse entries |
| 📋 Copyable | One-click copy to clipboard |
| ⏰ Timestamped | See when each transcription was made |
| 🔄 Auto-scroll | Newest entries at the top |
| 🎨 Polished | Hover effects and smooth interactions |
| ⚡ Fast | Handles 100+ entries smoothly |

## Integration

### Main App
The feature is already integrated! Just run:
```bash
voice-tui
```

Your transcriptions will automatically appear in the history log.

### How It Works
1. **You speak** → Whisper transcribes
2. **Text appears** → In status panel
3. **Auto-copy** → To clipboard
4. **Added to history** → Top of the log
5. **Click to expand** → See full text
6. **Click 📋** → Re-copy anytime

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Ctrl+Shift+Z** (hold) | Record audio |
| **C** | Clear history |
| **S** | Settings |
| **Q** | Quit |

## Tips & Tricks

### 💡 Tip 1: Quick Copy
Click the 📋 button on any entry to quickly re-copy old transcriptions.

### 💡 Tip 2: Click Anywhere
You can click anywhere on an entry to expand it, not just the arrow.

### 💡 Tip 3: Newest First
New transcriptions always appear at the top, so you see your latest work first.

### 💡 Tip 4: Clear When Needed
Press 'C' to clear all history and start fresh.

### 💡 Tip 5: Scroll Back
Use mouse wheel or arrow keys to scroll through older entries.

## Common Use Cases

### 📝 Quick Notes
Record short reminders and view them in the history.

### 📧 Email Drafts
Dictate email content, expand to review, then copy to paste.

### 📋 Meeting Notes
Record meeting discussions, expand to see details, copy to save.

### 💬 Messages
Dictate messages, review before sending, copy to clipboard.

### 📖 Documentation
Transcribe ideas, expand for full context, copy to docs.

## Customization

### Want More/Fewer Entries?
Edit `voice_tui/ui/history_log.py`:
```python
max_entries = 100  # Change to 50, 200, etc.
```

### Want Longer/Shorter Previews?
Edit `voice_tui/ui/history_entry.py`:
```python
preview = self.transcription[:80] + "..."  # Change 80
```

### Want Different Colors?
Edit `voice_tui/ui/styles.tcss` - all colors are customizable!

## FAQ

**Q: Is history saved between sessions?**
A: Not yet - this is a planned future enhancement.

**Q: Can I search the history?**
A: Not yet - search is on the roadmap.

**Q: Can I export history to a file?**
A: Not yet - export feature is coming in future updates.

**Q: How many entries can I have?**
A: Default is 100, but you can change this in the code.

**Q: Does this work with auto-type?**
A: Yes! Text is auto-typed AND added to history.

## What's Next?

Future enhancements planned:
- 💾 Persistent history (saved to disk)
- 🔍 Search & filter
- 📤 Export to file
- ✏️ Edit entries
- ⭐ Favorite/star entries
- 🏷️ Tags & categories

## Support

### Documentation
- [[HISTORY_FEATURE]] - Full feature documentation
- [[IMPLEMENTATION_SUMMARY]] - Technical details
- [[README]] - Main app documentation

### Testing
- `test_history.py` - Interactive demo app
- Test before deploying to production use

### Issues?
1. Check syntax: `python -m py_compile voice_tui/ui/*.py`
2. Verify imports: `python -c "from voice_tui.ui.history_log import HistoryLog"`
3. Run demo: `python test_history.py`

## Visual Examples

### Example 1: Short Entry
```
▶ 14:23:15  Buy groceries tonight 📋
```
Click to expand (no expansion needed - already fits in one line)

### Example 2: Long Entry (Collapsed)
```
▶ 14:22:08  This is a much longer transcription that will be truncated in th... 📋
```

### Example 2: Long Entry (Expanded)
```
▼ 14:22:08  This is a much longer transcription that will be truncated in th... 📋
    This is a much longer transcription that will be truncated in the
    preview. It contains multiple sentences and demonstrates how the
    collapsible history entries work when the text is very long.
```

### Example 3: Multiple Entries
```
▶ 14:25:10  Latest transcription here 📋
▶ 14:24:05  Another one before that 📋
▼ 14:23:00  This one is expanded to show full text content 📋
    This one is expanded to show full text content that is longer
    than the preview allows and needs to be shown in full detail.
▶ 14:22:00  And this is collapsed again 📋
```

## Start Using It Now!

```bash
# Run the main app
voice-tui

# Or
python -m voice_tui.main

# Try the demo
python test_history.py
```

**Enjoy your enhanced voice-to-text experience!** 🎤✨
