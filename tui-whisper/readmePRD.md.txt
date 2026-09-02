# PRD: Local Voice-to-Text TUI Application

Build a Terminal User Interface (TUI) application that records audio via hotkey, transcribes it using Whisper locally, and copies the result to clipboard.

## Core Requirements

### Functional Requirements
1. **Hotkey Recording**: Press Ctrl+Windows to start recording, release to stop
2. **Audio Processing**: Capture system microphone audio while hotkey is held
3. **Speech-to-Text**: Transcribe audio using OpenAI Whisper (local)
4. **Clipboard Output**: Copy transcribed text directly to system clipboard
5. **TUI Display**: Show real-time status in terminal interface

### Performance Requirements
- **Speed**: Use `faster-whisper` implementation (4x faster than vanilla Whisper)
- **Model**: Default to `base` model for speed, allow `medium` or `large-v3` via config for accuracy
- **Startup**: Model should load once at application start
- **Transcription**: Display progress/spinner during processing

### Platform Requirements
- **Target OS**: Cross-platform (Windows, macOS, Linux)
- **Installation**: Single command install via pip/pipx
- **Dependencies**: Minimal, self-contained

## Technical Specifications

### Technology Stack
- **Language**: Python 3.9+
- **TUI Framework**: `textual` or `rich` for terminal UI
- **STT Engine**: `faster-whisper` (optimized Whisper)
- **Audio Capture**: `sounddevice` + `numpy`
- **Hotkey Detection**: `keyboard` library (cross-platform)
- **Clipboard**: `pyperclip` (cross-platform)

### Core Dependencies
```
faster-whisper>=0.10.0
sounddevice>=0.4.6
numpy>=1.24.0
keyboard>=0.13.5
pyperclip>=1.8.2
textual>=0.40.0  # or rich>=13.0.0
```

## Interface Design

### TUI Layout
```
┌─────────────────────────────────────────┐
│  Voice-to-Text Transcription            │
├─────────────────────────────────────────┤
│  Status: [Idle / Recording / Processing]│
│  Model: base (loaded)                   │
│  Hotkey: Ctrl+Win                       │
├─────────────────────────────────────────┤
│  Last Transcription:                    │
│  [transcribed text appears here]        │
│  ✓ Copied to clipboard                  │
├─────────────────────────────────────────┤
│  Press Ctrl+Win to record               │
│  Press Ctrl+C to quit                   │
└─────────────────────────────────────────┘
```

### Status States
- **Idle**: Waiting for hotkey press
- **Recording**: Red indicator, timer showing duration
- **Processing**: Spinner/progress indicator
- **Complete**: Show transcribed text + checkmark

## Implementation Details

### Application Flow
1. **Startup**:
   - Load Whisper model (show loading spinner)
   - Initialize audio devices
   - Register hotkey listener
   - Display ready status

2. **Recording Cycle**:
   - Detect Ctrl+Win press → start recording
   - Show "Recording..." with timer
   - Capture audio buffer
   - Detect Ctrl+Win release → stop recording
   
3. **Processing**:
   - Show "Transcribing..." with spinner
   - Pass audio to Whisper
   - Display result in TUI
   - Copy to clipboard automatically
   - Return to Idle state

### Configuration File (Optional)
```yaml
# config.yaml
model: "base"  # base, small, medium, large-v3
language: "en"  # auto-detect if null
hotkey: "ctrl+win"
```

### Error Handling
- No microphone detected → display error, suggest fixes
- Model download needed → auto-download with progress bar
- Transcription failed → show error, keep last successful result
- Hotkey conflict → display warning, allow rebind

## File Structure
```
voice-to-text-tui/
├── README.md
├── pyproject.toml (or setup.py)
├── requirements.txt
├── voice_tui/
│   ├── __init__.py
│   ├── main.py          # Entry point
│   ├── recorder.py      # Audio capture
│   ├── transcriber.py   # Whisper wrapper
│   ├── ui.py            # TUI interface
│   └── config.py        # Config handling
└── config.yaml (optional)
```

## Installation & Usage

### Install
```bash
pip install voice-to-text-tui
# or
pipx install voice-to-text-tui
```

### Run
```bash
voice-tui
# or with config
voice-tui --model medium --language en
```

### First-Run Behavior
- Auto-download Whisper model if not present (show progress)
- Create default config if none exists
- Test microphone access

## Optimization Priorities

### Speed Optimizations
1. Use `faster-whisper` instead of vanilla Whisper
2. Default to `base` model (fastest while still accurate)
3. Keep model loaded in memory (no reload per transcription)
4. Trim silence from audio before transcription (VAD)
5. Use GPU if available (CUDA/Metal detection)

### Simplicity Priorities
1. Zero-config startup (works immediately)
2. Single command installation
3. No external services or API keys needed
4. Minimal dependencies
5. Clear, simple TUI (no overwhelming features)

## Non-Requirements (Keep Simple)
- ❌ No auto-paste (clipboard only)
- ❌ No cloud services
- ❌ No language auto-detection (default to English, configurable)
- ❌ No history/database
- ❌ No correction UI
- ❌ No multiple hotkeys

## Success Criteria
- [ ] Hotkey (Ctrl+Win) reliably starts/stops recording
- [ ] Transcription completes in <3 seconds for 10s audio
- [ ] Text accurately copied to clipboard
- [ ] TUI clearly shows current status
- [ ] Works on Windows, macOS, Linux
- [ ] Single-command install
- [ ] Can run continuously in background

## Deliverables
1. Fully working Python package
2. README with installation and usage instructions
3. Requirements.txt with pinned versions
4. Basic error handling for common issues

---

**Build this as a minimal, fast, reliable tool. Prioritize speed and simplicity over features.**