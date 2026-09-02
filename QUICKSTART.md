# Quick Start Guide

Get up and running with voice-tui in 5 minutes!

## Step 1: Install

```bash
# Navigate to project directory
cd tui-whisper

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install the package
pip install -e .
```

## Step 2: Test Installation

```bash
python test_install.py
```

This will verify:
- All dependencies are installed
- Your microphone is detected
- The package is properly configured

## Step 3: First Run

```bash
voice-tui
```

On first run:
- The Whisper model will download automatically (~140MB for base model)
- This only happens once
- Takes 1-5 minutes depending on your connection

## Step 4: Use It!

1. The TUI will launch showing "Status: Idle ✓"
2. Press and hold **Ctrl+Shift+Z**
3. Speak clearly into your microphone
4. Release **Ctrl+Shift+Z** when done
5. Wait for transcription (shows "Status: Processing...")
6. Your text appears and is copied to clipboard!
7. Paste anywhere with **Ctrl+V**

## Common First-Time Issues

### "No microphone detected"
- Check your microphone is plugged in
- Check Windows Settings > Privacy > Microphone
- Restart the app

### "Hotkey not working"
- Make sure the terminal window has focus
- On macOS/Linux, may need to run with `sudo voice-tui`
- Try alternative hotkey: `voice-tui --hotkey ctrl+alt`

### "Import errors"
- Run: `pip install -r requirements.txt`
- Make sure virtual environment is activated

## Tips for Best Results

1. **Speak clearly** - Enunciate your words
2. **Minimize background noise** - Find a quiet space
3. **Hold hotkey while speaking** - Don't release too early
4. **Wait for processing** - Takes 1-3 seconds for base model
5. **Use better model for accuracy** - `voice-tui --model small`

## Next Steps

- Read the full [README.md](README.md) for all features
- Create a `config.yaml` from `config.yaml.example` for persistent settings
- Try different models: `voice-tui --model tiny` (faster) or `voice-tui --model small` (more accurate)
- Check troubleshooting section if you encounter issues

## Example Workflow

```bash
# Start the app
voice-tui

# In the TUI:
# 1. Press and hold Ctrl+Win
# 2. Say: "This is a test of the voice to text application"
# 3. Release Ctrl+Win
# 4. Wait for transcription
# 5. Open any text editor
# 6. Press Ctrl+V to paste

# Result: "This is a test of the voice to text application." appears!
```

## Keyboard Shortcuts

- **Ctrl+Win** (hold): Record audio
- **Ctrl+C**: Quit application
- **Q**: Quit application

---

That's it! You're now ready to use voice-to-text transcription locally on your machine.

For more details, see the full [README.md](README.md).
