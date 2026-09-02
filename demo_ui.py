"""Demo script to preview the enhanced TUI without full setup."""

from voice_tui.config import Config
from voice_tui.ui.status_panel import StatusPanel
from voice_tui.ui.waveform import WaveformVisualizer
from voice_tui.ui.history_log import HistoryLog
from voice_tui.ui.main_screen import MainScreen
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
# Import the CSS from app_v2
from voice_tui.app_v2 import VoiceToTextApp as BaseApp
import asyncio


class DemoApp(App):
    """Demo app to showcase the new UI components."""

    # Use the same inline CSS as the main app
    CSS = BaseApp.CSS

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("1", "show_idle", "Idle State"),
        ("2", "show_recording", "Recording State"),
        ("3", "show_processing", "Processing State"),
        ("4", "show_complete", "Complete State"),
        ("5", "show_error", "Error State"),
    ]

    def __init__(self):
        super().__init__()
        self.title = "Voice-to-Text TUI - Demo"
        self.sub_title = "Press 1-5 to cycle through states"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield MainScreen()
        yield Footer()

    def on_mount(self) -> None:
        """Show initial state."""
        self.action_show_idle()

    def action_show_idle(self) -> None:
        """Show idle state."""
        status_panel = self.query_one(StatusPanel)
        status_panel.set_status("idle")
        self.notify("Showing: Idle State", severity="information")

    def action_show_recording(self) -> None:
        """Show recording state."""
        from voice_tui.ui.main_screen import MetricsRow

        status_panel = self.query_one(StatusPanel)
        waveform = self.query_one(WaveformVisualizer)
        metrics_row = self.query_one("#metrics-row", MetricsRow)

        status_panel.set_status("recording", duration=3.45)
        status_panel.audio_level = 0.65
        waveform.is_active = True
        waveform.add_class("active")
        metrics_row.add_class("visible")
        metrics_row.update_metrics(3.45, 0.65)

        self.notify("Showing: Recording State", severity="information")

    def action_show_processing(self) -> None:
        """Show processing state."""
        from voice_tui.ui.main_screen import MetricsRow

        status_panel = self.query_one(StatusPanel)
        waveform = self.query_one(WaveformVisualizer)
        metrics_row = self.query_one("#metrics-row", MetricsRow)

        status_panel.set_status("processing")
        waveform.is_active = False
        waveform.remove_class("active")
        metrics_row.remove_class("visible")

        self.notify("Showing: Processing State", severity="information")

    def action_show_complete(self) -> None:
        """Show complete state."""
        status_panel = self.query_one(StatusPanel)
        history_log = self.query_one(HistoryLog)

        status_panel.set_status("complete", "This is a sample transcription that was just completed!")
        history_log.add_entry("This is a sample transcription that was just completed!")

        self.notify("Showing: Complete State", severity="information")

    def action_show_error(self) -> None:
        """Show error state."""
        status_panel = self.query_one(StatusPanel)

        status_panel.set_status("error", "Microphone not detected")

        self.notify("Showing: Error State", severity="error")


if __name__ == "__main__":
    app = DemoApp()
    app.run()
