# VOICE-TO-TEXT TUI - IMPLEMENTATION PROMPT
## Visual-First Specification Based on Reference Screenshots

---

## VISUAL REFERENCE ANALYSIS

Based on the screenshot showing the desired UI (Screenshot 2026-02-01 155759.png), the interface follows this exact layout:

```
┌─────────────────────────────────────────────────────────────────┐
│ Voice-to-Text TUI          [Status: Ready]          │  Header   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│    ┌───────────────────────────────────────────────────────┐   │
│    │                                                       │   │
│    │            ● READY TO RECORD                          │   │  Status Panel
│    │                                                       │   │  (centered, bordered)
│    │            Hold [Ctrl+Win] to record                  │   │
│    │                                                       │   │
│    └───────────────────────────────────────────────────────┘   │
│                                                                 │
│    ┌───────────────────────────────────────────────────────┐   │
│    │  ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁  [Waveform Visualization]           │   │  Waveform
│    │                                                       │   │  (only when recording)
│    └───────────────────────────────────────────────────────┘   │
│                                                                 │
│         Recording: 00:03.45  │  Level: ████░░░░░░ 45%           │  Metrics Row
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  Recent Transcriptions:                                         │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ 14:32:15  "This is the most recent transcription..."     │ │  History Log
│  │ 14:28:42  "Another transcription example here..."        │ │  (scrollable)
│  │ 14:15:03  "Earlier transcription text..."                │ │
│  └───────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  [Ctrl+Win] Record  │  [Q] Quit  │  [S] Settings  │  [C] Clear │  Footer
└─────────────────────────────────────────────────────────────────┘
```

---

## LAYOUT SPECIFICATIONS

### 1. HEADER
- **Height**: 1 row
- **Content**: 
  - Left: "Voice-to-Text TUI" (app title)
  - Center: "[Status: Ready]" (dynamic status)
  - Right: Clock (HH:MM:SS format)
- **Style**: Dark background, subtle border-bottom

### 2. STATUS PANEL (Main Focus Area)
- **Position**: Top-center of main content
- **Width**: ~80% of screen width
- **Height**: 8-10 rows
- **Border**: Double-line or heavy border
- **Content Alignment**: Center both horizontal and vertical
- **States**:
  - **IDLE**: Green dot (●) + "READY TO RECORD" + instruction line
  - **RECORDING**: Red pulsing dot + "RECORDING" + live timer
  - **PROCESSING**: Yellow spinner + "TRANSCRIBING..."
  - **COMPLETE**: Green checkmark + "COMPLETE" + text preview
  - **ERROR**: Red X + error message

### 3. WAVEFORM VISUALIZER
- **Position**: Below status panel
- **Width**: Same as status panel (~80%)
- **Height**: 5 rows
- **Visibility**: Only visible during recording
- **Content**: ASCII waveform visualization (▁▂▃▄▅▆▇█▇▆▅▄▃▂▁ style)
- **Border**: Single line border

### 4. METRICS ROW
- **Position**: Below waveform
- **Content**: 
  - Left: "Recording: 00:03.45" (timer)
  - Right: "Level: ████░░░░░░ 45%" (audio level bar)
- **Visibility**: Only during recording
- **Style**: Plain text, no border

### 5. HISTORY LOG
- **Position**: Below metrics row
- **Width**: ~90% of screen width
- **Height**: 10-12 rows or flexible
- **Header**: "Recent Transcriptions:" label above
- **Border**: Single line border around list area
- **Content Format**: "HH:MM:SS  \"transcription text...\""
- **Scrollable**: Yes, with scrollbar
- **Max Entries**: 100 (auto-remove oldest)

### 6. FOOTER
- **Height**: 1 row
- **Position**: Bottom docked
- **Background**: Distinct color (blue/cyan accent)
- **Content**: Keyboard shortcuts
  - "[Ctrl+Win] Record"
  - "[Q] Quit"
  - "[S] Settings"
  - "[C] Clear"
- **Style**: Bracketed keys, clear spacing

---

## COLOR SCHEME

### Dark Theme (Default)
```
Background:     #0f172a  (Slate 900 - very dark blue-gray)
Surface:        #1e293b  (Slate 800 - panel backgrounds)
Panel:          #334155  (Slate 700 - borders)

Text Primary:   #f8fafc  (Slate 50 - white)
Text Secondary: #94a3b8  (Slate 400 - muted)

Success:        #10b981  (Emerald 500 - green)
Warning:        #f59e0b  (Amber 500 - yellow/orange)
Error:          #ef4444  (Red 500)
Accent:         #06b6d4  (Cyan 500 - footer)

Recording Glow: #ef4444 30% (subtle red tint during recording)
```

### State Colors
- **Idle**: Green border/text
- **Recording**: Red border/text with background tint
- **Processing**: Yellow/Orange border/text
- **Complete**: Green border/text
- **Error**: Red border/text

---

## TEXTUAL CSS (styles.tcss)

```css
/* Base Screen */
Screen {
    background: #0f172a;
    color: #f8fafc;
}

/* Header */
Header {
    background: #1e293b;
    color: #f8fafc;
    border-bottom: solid #334155;
}
Header.-tall {
    height: auto;
}

/* Main Layout Container */
#main-container {
    width: 100%;
    height: 100%;
    padding: 1 2;
}

/* Status Panel */
StatusPanel {
    width: 80%;
    height: auto;
    min-height: 8;
    border: double green;
    background: #1e293b;
    content-align: center middle;
    margin: 1 auto;
    padding: 1 2;
}
StatusPanel.idle {
    border: double #10b981;
}
StatusPanel.recording {
    border: heavy #ef4444;
    background: #ef4444 10%;
}
StatusPanel.processing {
    border: solid #f59e0b;
}
StatusPanel.complete {
    border: solid #10b981;
}
StatusPanel.error {
    border: heavy #ef4444;
}

/* Status Indicator */
#status-indicator {
    text-align: center;
    color: auto;
}

/* Status Text */
#status-text {
    text-align: center;
    text-style: bold;
}

/* Instruction Text */
#instruction-text {
    text-align: center;
    color: #94a3b8;
}

/* Waveform Visualizer */
WaveformVisualizer {
    width: 80%;
    height: 5;
    border: solid #334155;
    background: #0f172a;
    margin: 1 auto;
    display: none;
}
WaveformVisualizer.active {
    display: block;
}

/* Metrics Row */
MetricsRow {
    width: 80%;
    height: auto;
    content-align: center middle;
    margin: 0 auto;
    display: none;
}
MetricsRow.visible {
    display: block;
}

/* Timer Display */
#timer-display {
    color: #f8fafc;
}

/* Level Meter */
#level-meter {
    color: auto;
}

/* History Section */
#history-label {
    margin: 1 0 0 5%;
    color: #94a3b8;
}

HistoryLog {
    width: 90%;
    height: 12;
    border: solid #334155;
    background: #1e293b;
    margin: 0 auto 1 auto;
    padding: 0 1;
}

/* History Entry */
.history-entry {
    color: #f8fafc;
    margin: 0 0 1 0;
}
.history-timestamp {
    color: #94a3b8;
}
.history-text {
    color: #f8fafc;
}

/* Footer / Shortcuts Bar */
#shortcuts-bar {
    dock: bottom;
    height: 1;
    background: #0369a1;
    color: white;
    content-align: center middle;
}

/* Footer */
Footer {
    background: #0369a1;
    color: white;
}
FooterKey {
    background: #0369a1;
    color: white;
}
FooterKeyDescription {
    background: #0369a1;
    color: white;
}
```

---

## WIDGET IMPLEMENTATIONS

### StatusPanel Widget

```python
from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
from rich.align import Align

class StatusPanel(Static):
    """Main status display with state-aware rendering"""
    
    status = reactive("idle")
    duration = reactive(0.0)
    message = reactive("")
    
    def watch_status(self, status: str) -> None:
        """Update CSS class when status changes"""
        self.remove_class("idle", "recording", "processing", "complete", "error")
        self.add_class(status)
        self.update(self._render_content())
    
    def watch_duration(self, duration: float) -> None:
        """Update display when duration changes"""
        if self.status == "recording":
            self.update(self._render_content())
    
    def watch_message(self, message: str) -> None:
        """Update display when message changes"""
        self.update(self._render_content())
    
    def _render_content(self) -> Text:
        """Render content based on current state"""
        if self.status == "idle":
            return self._render_idle()
        elif self.status == "recording":
            return self._render_recording()
        elif self.status == "processing":
            return self._render_processing()
        elif self.status == "complete":
            return self._render_complete()
        elif self.status == "error":
            return self._render_error()
        return Text("Unknown state")
    
    def _render_idle(self) -> Text:
        lines = [
            Text(""),
            Text.assemble(
                ("● ", "bold green"),
                ("READY TO RECORD", "bold white")
            ),
            Text(""),
            Text("Hold [Ctrl+Win] to record", style="dim")
        ]
        return Text("\n").join(lines)
    
    def _render_recording(self) -> Text:
        lines = [
            Text(""),
            Text.assemble(
                ("● ", "bold red"),
                ("RECORDING", "bold red")
            ),
            Text(""),
            Text(f"Duration: {self.duration:.2f}s", style="white")
        ]
        return Text("\n").join(lines)
    
    def _render_processing(self) -> Text:
        spinner = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"[int(self.app.current_time * 10) % 10]
        lines = [
            Text(""),
            Text.assemble(
                (f"{spinner} ", "bold yellow"),
                ("TRANSCRIBING...", "bold yellow")
            ),
            Text(""),
            Text("Processing audio with Whisper", style="dim")
        ]
        return Text("\n").join(lines)
    
    def _render_complete(self) -> Text:
        preview = self.message[:50] + "..." if len(self.message) > 50 else self.message
        lines = [
            Text(""),
            Text.assemble(
                ("✓ ", "bold green"),
                ("TRANSCRIPTION COMPLETE", "bold green")
            ),
            Text(""),
            Text(preview, style="white"),
            Text(""),
            Text("Copied to clipboard ✓", style="dim green")
        ]
        return Text("\n").join(lines)
    
    def _render_error(self) -> Text:
        lines = [
            Text(""),
            Text.assemble(
                ("✗ ", "bold red"),
                ("ERROR", "bold red")
            ),
            Text(""),
            Text(self.message, style="white"),
            Text(""),
            Text("Press any key to dismiss", style="dim")
        ]
        return Text("\n").join(lines)
    
    def set_status(self, status: str, message: str = "") -> None:
        """Set status and optional message"""
        self.status = status
        self.message = message
```

### WaveformVisualizer Widget

```python
from textual.widget import Widget
from textual.reactive import reactive
from textual.strip import Strip
from textual._segment_tools import line_crop
import numpy as np

class WaveformVisualizer(Widget):
    """Real-time audio waveform display"""
    
    audio_data = reactive(np.array([]))
    is_active = reactive(False)
    
    def __init__(self):
        super().__init__()
        self.waveform_history = []
        self.max_history = 100
    
    def watch_is_active(self, active: bool) -> None:
        """Show/hide based on active state"""
        if active:
            self.add_class("active")
        else:
            self.remove_class("active")
            self.waveform_history = []
    
    def add_sample(self, amplitude: float) -> None:
        """Add new audio sample to waveform"""
        self.waveform_history.append(amplitude)
        if len(self.waveform_history) > self.max_history:
            self.waveform_history.pop(0)
        self.refresh()
    
    def render_line(self, y: int) -> Strip:
        """Render a line of the waveform"""
        if not self.waveform_history:
            return Strip.blank(self.size.width)
        
        # Map y position to waveform amplitude
        height = self.size.height
        center = height // 2
        
        if y == center:
            # Center line - draw waveform
            chars = []
            for i, amp in enumerate(self.waveform_history[-self.size.width:]):
                # Determine character based on amplitude
                bar_chars = " ▁▂▃▄▅▆▇█"
                idx = int(abs(amp) * (len(bar_chars) - 1))
                chars.append(bar_chars[min(idx, len(bar_chars) - 1)])
            
            from rich.segment import Segment
            segments = [Segment(c, self.get_component_rich_style("waveform")) for c in chars]
            return Strip(segments)
        
        return Strip.blank(self.size.width)
```

### AudioLevelMeter (Inline in MetricsRow)

```python
class MetricsRow(Static):
    """Display recording metrics (timer + level)"""
    
    duration = reactive(0.0)
    level = reactive(0.0)
    
    def render(self) -> Text:
        # Format timer
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        ms = int((self.duration % 1) * 100)
        timer = f"{minutes:02d}:{seconds:02d}.{ms:02d}"
        
        # Format level bar
        filled = int(self.level * 10)
        bar = "█" * filled + "░" * (10 - filled)
        
        # Color based on level
        if self.level < 0.4:
            bar_color = "green"
        elif self.level < 0.7:
            bar_color = "yellow"
        else:
            bar_color = "red"
        
        return Text.assemble(
            ("Recording: ", "white"),
            (timer, "cyan"),
            ("  │  ", "dim"),
            ("Level: ", "white"),
            (bar, bar_color),
            (f" {self.level*100:.0f}%", "dim")
        )
```

### HistoryLog Widget

```python
from textual.widgets import Static
from textual.reactive import reactive
from collections import deque
from datetime import datetime

class HistoryLog(Static):
    """Scrollable transcription history"""
    
    entries = reactive(deque(maxlen=100))
    
    def add_entry(self, text: str) -> None:
        """Add new transcription entry"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.entries.append({"time": timestamp, "text": text})
        self.update(self._render_entries())
    
    def clear(self) -> None:
        """Clear all entries"""
        self.entries.clear()
        self.update(self._render_entries())
    
    def _render_entries(self) -> Text:
        if not self.entries:
            return Text("No transcriptions yet", style="dim")
        
        lines = []
        for entry in self.entries:
            line = Text.assemble(
                (entry["time"], "dim"),
                ("  \"", "white"),
                (entry["text"][:60], "white"),
                ("\"", "white")
            )
            lines.append(line)
        
        return Text("\n").join(lines)
```

### MainScreen Composition

```python
from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import Static, Header, Footer

class MainScreen(Screen):
    """Main application screen"""
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Vertical(id="main-container"):
            # Status Panel
            yield StatusPanel()
            
            # Waveform (hidden by default)
            yield WaveformVisualizer()
            
            # Metrics Row (hidden by default)
            yield MetricsRow(id="metrics-row")
            
            # History Label
            yield Static("Recent Transcriptions:", id="history-label")
            
            # History Log
            yield HistoryLog()
        
        # Shortcuts Bar
        yield Static(
            "[Ctrl+Win] Record  │  [Q] Quit  │  [S] Settings  │  [C] Clear",
            id="shortcuts-bar"
        )
        
        yield Footer()
```

---

## MAIN APPLICATION

```python
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual import work
import pyperclip

class VoiceToTextApp(App):
    """Voice-to-Text TUI Application"""
    
    CSS_PATH = "ui/styles.tcss"
    
    # Reactive state
    current_status = reactive("idle")
    recording_duration = reactive(0.0)
    audio_level = reactive(0.0)
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "settings", "Settings"),
        ("c", "clear_history", "Clear"),
    ]
    
    def __init__(self, config_path: str = "config.yaml"):
        super().__init__()
        self.config = Config.load(config_path)
        self.recorder = AudioRecorder()
        self.transcriber = WhisperTranscriber(self.config.model_name)
        self.hotkey_handler = None
        self.recording_start_time = None
    
    def compose(self) -> ComposeResult:
        yield MainScreen()
    
    def on_mount(self) -> None:
        """Initialize on mount"""
        self.title = "Voice-to-Text TUI"
        self.sub_title = f"Model: {self.config.model_name} | Hotkey: {self.config.hotkey}"
        
        # Start hotkey listener
        self.hotkey_handler = HotkeyHandler(
            self.config.hotkey,
            on_press=self._on_hotkey_press,
            on_release=self._on_hotkey_release
        )
        self.hotkey_handler.start()
        
        # Set initial state
        self.set_status("idle")
    
    def set_status(self, status: str, message: str = "") -> None:
        """Update application status"""
        self.current_status = status
        status_panel = self.query_one(StatusPanel)
        status_panel.set_status(status, message)
        
        # Update header status
        status_map = {
            "idle": "Ready",
            "recording": "Recording",
            "processing": "Processing",
            "complete": "Complete",
            "error": "Error"
        }
        self.sub_title = f"[Status: {status_map.get(status, status)}] | Model: {self.config.model_name}"
    
    def _on_hotkey_press(self) -> None:
        """Handle hotkey press"""
        if self.current_status == "idle":
            self.action_start_recording()
    
    def _on_hotkey_release(self) -> None:
        """Handle hotkey release"""
        if self.current_status == "recording":
            self.action_stop_recording()
    
    @work(thread=True)
    def action_start_recording(self) -> None:
        """Start recording"""
        self.set_status("recording")
        self.recording_start_time = self.current_time
        
        # Show waveform and metrics
        waveform = self.query_one(WaveformVisualizer)
        metrics = self.query_one(MetricsRow)
        waveform.is_active = True
        metrics.add_class("visible")
        
        # Start audio recording
        self.recorder.start()
        
        # Start duration timer
        self.set_interval(0.1, self._update_recording_metrics)
    
    def _update_recording_metrics(self) -> None:
        """Update recording timer and audio level"""
        if self.current_status != "recording":
            return
        
        # Update duration
        if self.recording_start_time:
            self.recording_duration = self.current_time - self.recording_start_time
        
        # Update audio level from recorder
        self.audio_level = self.recorder.get_current_level()
        
        # Update metrics display
        metrics = self.query_one(MetricsRow)
        metrics.duration = self.recording_duration
        metrics.level = self.audio_level
        
        # Add to waveform
        waveform = self.query_one(WaveformVisualizer)
        waveform.add_sample(self.audio_level)
    
    @work(thread=True)
    def action_stop_recording(self) -> None:
        """Stop recording and transcribe"""
        # Stop recorder
        audio_data = self.recorder.stop()
        
        # Hide waveform and metrics
        waveform = self.query_one(WaveformVisualizer)
        metrics = self.query_one(MetricsRow)
        waveform.is_active = False
        metrics.remove_class("visible")
        
        # Check minimum duration
        if self.recording_duration < self.config.min_duration:
            self.notify("Recording too short", severity="warning")
            self.set_status("idle")
            return
        
        # Transcribe
        self.set_status("processing")
        
        try:
            text = self.transcriber.transcribe(audio_data)
            
            # Copy to clipboard
            pyperclip.copy(text)
            
            # Update UI
            self.call_from_thread(self._on_transcription_complete, text)
            
        except Exception as e:
            self.call_from_thread(self.set_status, "error", str(e))
    
    def _on_transcription_complete(self, text: str) -> None:
        """Handle completed transcription"""
        self.set_status("complete", text)
        
        # Add to history
        history = self.query_one(HistoryLog)
        history.add_entry(text)
        
        # Notify
        self.notify("Copied to clipboard!", severity="information")
        
        # Return to idle after delay
        self.set_timer(2, lambda: self.set_status("idle"))
    
    def action_settings(self) -> None:
        """Open settings modal"""
        self.push_screen(SettingsModal())
    
    def action_clear_history(self) -> None:
        """Clear transcription history"""
        history = self.query_one(HistoryLog)
        history.clear()
        self.notify("History cleared", severity="information")
    
    def on_unmount(self) -> None:
        """Cleanup on exit"""
        if self.hotkey_handler:
            self.hotkey_handler.stop()
```

---

## SETTINGS MODAL

```python
from textual.screen import ModalScreen
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Label, Select, Static

class SettingsModal(ModalScreen):
    """Settings configuration modal"""
    
    DEFAULT_CSS = """
    SettingsModal {
        align: center middle;
    }
    #settings-container {
        width: 60;
        height: auto;
        background: #1e293b;
        border: solid #6366f1;
        padding: 1 2;
    }
    #settings-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    .setting-row {
        height: auto;
        margin: 1 0;
    }
    .setting-label {
        color: #94a3b8;
    }
    #button-row {
        height: auto;
        margin-top: 2;
        content-align: center middle;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Vertical(id="settings-container"):
            yield Static("Settings", id="settings-title")
            
            # Model selection
            with Vertical(classes="setting-row"):
                yield Static("Whisper Model:", classes="setting-label")
                yield Select(
                    [(m, m) for m in ["tiny", "base", "small", "medium", "large-v3"]],
                    value=self.app.config.model_name,
                    id="model-select"
                )
            
            # Language
            with Vertical(classes="setting-row"):
                yield Static("Language (e.g., en, es, fr):", classes="setting-label")
                yield Input(value=self.app.config.language, id="language-input")
            
            # Hotkey
            with Vertical(classes="setting-row"):
                yield Static("Hotkey (e.g., ctrl+win):", classes="setting-label")
                yield Input(value=self.app.config.hotkey, id="hotkey-input")
            
            # Min duration
            with Vertical(classes="setting-row"):
                yield Static("Min recording duration (seconds):", classes="setting-label")
                yield Input(value=str(self.app.config.min_duration), id="duration-input")
            
            # Buttons
            with Horizontal(id="button-row"):
                yield Button("Save", variant="primary", id="save-btn")
                yield Button("Cancel", id="cancel-btn")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "save-btn":
            self._save_settings()
        else:
            self.dismiss()
    
    def _save_settings(self) -> None:
        """Save settings to config"""
        model = self.query_one("#model-select", Select).value
        language = self.query_one("#language-input", Input).value
        hotkey = self.query_one("#hotkey-input", Input).value
        duration = float(self.query_one("#duration-input", Input).value or 0.5)
        
        self.app.config.model_name = model
        self.app.config.language = language
        self.app.config.hotkey = hotkey
        self.app.config.min_duration = duration
        self.app.config.save()
        
        self.notify("Settings saved!", severity="information")
        self.dismiss()
```

---

## FILE STRUCTURE

```
voice_tui/
├── __init__.py
├── main.py              # Entry point
├── app.py               # Main Textual App
├── config.py            # Configuration management
├── recorder.py          # Audio capture
├── transcriber.py       # Whisper transcription
├── hotkey.py            # Global hotkey handler
└── ui/
    ├── __init__.py
    ├── styles.tcss        # CSS styles
    ├── main_screen.py     # Screen composition
    ├── status_panel.py    # Status widget
    ├── waveform.py        # Waveform widget
    ├── history_log.py     # History widget
    ├── metrics_row.py     # Timer/level display
    └── settings_modal.py  # Settings modal
```

---

## IMPLEMENTATION PRIORITIES

### Phase 1: Layout Foundation
1. Create `styles.tcss` with exact layout from screenshot
2. Implement `MainScreen` with all containers
3. Implement `StatusPanel` with all 5 states
4. Test layout rendering

### Phase 2: Core Widgets
1. Implement `WaveformVisualizer` (ASCII style)
2. Implement `MetricsRow` (timer + level meter)
3. Implement `HistoryLog` (scrollable list)
4. Test widget integration

### Phase 3: Application Logic
1. Implement `VoiceToTextApp` with state management
2. Integrate `AudioRecorder` and `WhisperTranscriber`
3. Add hotkey handling
4. Test full recording flow

### Phase 4: Polish
1. Implement `SettingsModal`
2. Add notifications
3. Fine-tune animations
4. Cross-platform testing

---

## VISUAL VALIDATION CHECKLIST

- [ ] Header shows title, status, and clock
- [ ] Status Panel is centered with proper border
- [ ] Status text is centered both horizontally and vertically
- [ ] Waveform appears only during recording
- [ ] Metrics row shows timer and level meter
- [ ] History section has label and bordered list
- [ ] Footer has blue background with shortcuts
- [ ] State transitions are smooth and visible
- [ ] Colors match the dark theme specification
- [ ] All text is readable and properly aligned

---

## KEY DESIGN PRINCIPLES

1. **Visual Hierarchy**: Status Panel is the focal point, largest and centered
2. **State Clarity**: Each state has distinct colors and indicators
3. **Minimal Animation**: Subtle pulsing for recording, spinner for processing
4. **Consistent Spacing**: Even margins and padding throughout
5. **Readable Typography**: Clear contrast, appropriate text sizes
6. **Functional Layout**: Information organized by importance and usage frequency
