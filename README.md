# Voice-to-Text TUI Application

A Terminal User Interface (TUI) application that records audio via hotkey, transcribes it using Whisper locally, and copies the result to your clipboard. All processing happens on your machine - no cloud services required.

## Features

- **Hotkey Recording**: Press and hold Ctrl+Shift+Z to record audio (push-to-talk)
- **Local Transcription**: Uses faster-whisper for fast, accurate transcription
- **Auto-Clipboard**: Transcribed text is automatically copied to clipboard
- **Real-time UI**: Clean TUI shows recording status, duration, and results
- **Privacy-First**: All processing happens locally on your machine
- **Configurable**: Choose model size, language, and hotkey combination

## Requirements

- Python 3.8 or higher
- Microphone
- ~500MB disk space (for Whisper models)

### Platform-Specific Requirements

**Windows:**
- No special requirements
- Microphone permissions in Settings > Privacy > Microphone

**macOS:**
- Accessibility permissions for keyboard library
- Microphone permissions in System Preferences > Security & Privacy

**Linux:**
- May require root/sudo for global hotkey functionality
- ALSA/PulseAudio for audio recording

## Installation

### 1. Clone or Download

```bash
cd tui-whisper
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install the Package

```bash
pip install -e .
```

Or install dependencies directly:

```bash
pip install -r requirements.txt
```

### 4. First Run

On first run, the Whisper model will be downloaded automatically (~140MB for base model). This only happens once.

## Usage

### Basic Usage

Simply run:

```bash
voice-tui
```

Or if not installed as a package:

```bash
python -m voice_tui.main
```

### Controls

- **Ctrl+Shift+Z** (hold): Start/stop recording
- **Ctrl+C** or **Q**: Quit application

### Command-Line Options

```bash
voice-tui [OPTIONS]

Options:
  --model TEXT       Whisper model size (tiny, base, small, medium, large-v3)
                     Default: base
  --language TEXT    Language code (en, es, fr, de, etc.)
                     Default: en
  --hotkey TEXT      Hotkey combination (e.g., 'ctrl+win', 'ctrl+alt')
                     Default: ctrl+win
  --config PATH      Path to config.yaml file
                     Default: ./config.yaml
```

### Examples

Use a smaller model for faster transcription:
```bash
voice-tui --model tiny
```

Transcribe Spanish audio:
```bash
voice-tui --language es
```

Use a different hotkey:
```bash
voice-tui --hotkey ctrl+alt
```

Use a larger model for better accuracy (requires more RAM):
```bash
voice-tui --model medium
```

## Configuration File

Create a `config.yaml` file in your working directory for persistent settings:

```yaml
# Whisper model size (tiny, base, small, medium, large-v2, large-v3)
model_name: base

# Language code (en, es, fr, de, etc.)
language: en

# Hotkey combination
hotkey: ctrl+win

# Audio sample rate (Hz)
sample_rate: 16000

# Minimum recording duration (seconds)
min_recording_duration: 0.5

# Device type (auto, cpu, cuda)
device_type: auto

# Compute type (auto, int8, float16, float32)
compute_type: auto
```

Command-line arguments override config file settings.

## Model Sizes

| Model | Size | RAM Required | Speed | Accuracy |
|-------|------|--------------|-------|----------|
| tiny | ~75MB | ~1GB | Fastest | Good |
| base | ~140MB | ~1GB | Very Fast | Better |
| small | ~460MB | ~2GB | Fast | Great |
| medium | ~1.5GB | ~5GB | Moderate | Excellent |
| large-v3 | ~3GB | ~10GB | Slow | Best |

**Recommendation**: Start with `base` for a good balance of speed and accuracy.

## Troubleshooting

### No Microphone Detected

**Problem**: Error message about no microphone found.

**Solutions**:
1. Check that your microphone is connected
2. Check system audio settings (make sure it's not muted)
3. Grant microphone permissions:
   - Windows: Settings > Privacy > Microphone
   - macOS: System Preferences > Security & Privacy > Microphone
   - Linux: Check PulseAudio/ALSA configuration

### Hotkey Not Working

**Problem**: Pressing Ctrl+Shift+Z doesn't start recording.

**Solutions**:

**Windows**:
- Make sure the application window has focus
- Check if another application is using the same hotkey
- Try a different hotkey with `--hotkey ctrl+alt`

**macOS**:
- Grant Accessibility permissions:
  - System Preferences > Security & Privacy > Privacy > Accessibility
  - Add Terminal or your terminal emulator to the list
- May need to run with `sudo` for global hotkey

**Linux**:
- May need to run with `sudo`:
  ```bash
  sudo voice-tui
  ```
- Or configure udev rules for keyboard access without root
- Alternatively, use when terminal has focus

### Model Download Fails

**Problem**: Error during model download on first run.

**Solutions**:
1. Check your internet connection
2. Ensure you have enough disk space (~500MB minimum)
3. Try again - downloads can resume if interrupted
4. Try a smaller model: `voice-tui --model tiny`

### Transcription Too Slow

**Problem**: Processing takes too long after recording.

**Solutions**:
1. Use a smaller model: `voice-tui --model tiny`
2. If you have an NVIDIA GPU, install CUDA support:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```
3. Close other applications to free up RAM

### "Recording Too Short" Message

**Problem**: Message appears after very quick press.

**Solution**: Hold the hotkey for at least 0.5 seconds while speaking.

### Clipboard Not Working

**Problem**: Text not copied to clipboard.

**Solutions**:
1. Install clipboard dependencies:
   - Linux: `sudo apt-get install xclip` or `xsel`
   - macOS/Windows: Should work out of the box
2. Check clipboard permissions in system settings

### Permission Errors

**Linux/macOS**: If you get permission errors for keyboard:

```bash
# Run with sudo (temporary solution)
sudo voice-tui

# OR configure udev rules (permanent solution for Linux)
# See: https://github.com/boppreh/keyboard#linux
```

## How It Works

1. **Hotkey Detection**: Global keyboard listener detects Ctrl+Shift+Z press
2. **Audio Recording**: Captures microphone audio at 16kHz while hotkey is held
3. **Transcription**: Uses faster-whisper to transcribe audio locally
4. **Clipboard**: Copies transcribed text to system clipboard
5. **Display**: Shows result in TUI with status indicator

## Architecture

```
voice_tui/
├── main.py          - Entry point, orchestration, hotkey handling
├── config.py        - Configuration management
├── recorder.py      - Audio capture with sounddevice
├── transcriber.py   - Whisper transcription wrapper
└── ui.py            - Textual TUI interface
```

## Dependencies

- **faster-whisper**: Fast Whisper implementation with CTranslate2
- **sounddevice**: Cross-platform audio recording
- **keyboard**: Global hotkey detection
- **pyperclip**: Cross-platform clipboard access
- **textual**: Modern TUI framework
- **numpy**: Audio data processing
- **PyYAML**: Configuration file parsing

## Performance Tips

1. **GPU Acceleration**: Install PyTorch with CUDA for 2-3x speedup on NVIDIA GPUs
2. **Model Selection**: Use `tiny` or `base` for real-time feel
3. **RAM**: Ensure sufficient RAM for chosen model (see table above)
4. **Close Background Apps**: Free up CPU/RAM for better performance

## Privacy & Security

- **100% Local**: No data sent to cloud services
- **No Internet Required**: After initial model download
- **No Telemetry**: No usage tracking or analytics
- **Open Source**: Inspect the code yourself

## Known Limitations

- Global hotkey requires special permissions on macOS/Linux
- Cannot record while other apps use the microphone exclusively
- Transcription accuracy depends on:
  - Audio quality (clear speech works best)
  - Model size (larger = more accurate)
  - Language support (English is best supported)

## Future Enhancements

Planned features (not in MVP):
- Multiple hotkey support
- Transcription history
- Auto-paste functionality
- Background daemon mode
- Language auto-detection
- Custom vocabulary/commands

## Contributing

This is an MVP implementation. Contributions welcome for:
- Bug fixes
- Platform-specific improvements
- Documentation improvements
- Feature enhancements (from roadmap above)

## License

MIT License - See LICENSE file for details

## Credits

Built with:
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper) by Guillaume Klein
- [OpenAI Whisper](https://github.com/openai/whisper) models
- [Textual](https://github.com/Textualize/textual) by Textualize

## Support

For issues, questions, or suggestions:
1. Check the Troubleshooting section above
2. Review existing GitHub issues
3. Open a new issue with:
   - Your platform (Windows/macOS/Linux)
   - Python version
   - Full error message
   - Steps to reproduce

---

Made with ❤️ for privacy-conscious users who want local voice-to-text.
