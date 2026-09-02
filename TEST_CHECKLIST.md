# Testing Checklist

## Fixed Issue
✅ **"VoiceToTextApp has no attribute 'set_state'"** - Changed to use `set_status` method

## How to Test

### 1. Quick Import Test
```bash
python -c "from voice_tui.main import VoiceToTextController; print('OK')"
```

### 2. Run Demo (No Microphone Needed)
```bash
python demo_ui.py
```
- Press `1` - Should show idle state with centered green box
- Press `2` - Should show recording state with waveform + metrics
- Press `3` - Should show processing spinner
- Press `4` - Should add to history
- Press `Q` - Quit

### 3. Run Full App
```bash
voice-tui
```

**Expected:**
- App starts and shows the TUI dashboard
- Green centered status panel says "READY TO RECORD"
- No waveform or metrics visible (hidden)
- History section at bottom (empty)
- Shortcuts bar at very bottom

### 4. Test Recording
1. Press and hold `Ctrl+Win`
2. **Should see:**
   - Status panel turns red
   - Waveform appears
   - Metrics row appears showing timer
3. Speak into microphone
4. Release `Ctrl+Win`
5. **Should see:**
   - Processing spinner
   - Then success message
   - Notification about clipboard
   - Entry added to history

## If You Still Get Errors

### Error: "No module named 'voice_tui'"
```bash
# Make sure you're in the right directory
cd C:\Users\Hp\Documents\tui-whisper

# Try reinstalling
pip install -e .
```

### Error: "Cannot find StatusPanel"
```bash
# Reinstall to update imports
pip install -e .
```

### The dashboard doesn't show
This usually means the app crashed before showing the UI. Check:
1. Is there an error message before "Goodbye!"?
2. Try the demo first: `python demo_ui.py`

### Still having issues?
Run with debug output:
```bash
python -m voice_tui.main 2>&1 | tee debug.log
```

Then check `debug.log` for the full error message.

## What Fixed

- Line 188 in `main.py` was calling `self.app.set_state(AppState.IDLE)`
- Changed to: removed (handled automatically by `set_transcription`)
- This matches the new app.py API which uses `set_status("idle")` instead
