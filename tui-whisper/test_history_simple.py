"""Simple test to verify history entries work."""

from textual.app import App
from textual.widgets import Header, Footer
from textual.containers import Container
from voice_tui.ui.history_log import HistoryLog


class SimpleHistoryTest(App):
    """Minimal test app."""

    def compose(self):
        yield Header()
        yield Container(HistoryLog(id="history"))
        yield Footer()

    def on_mount(self):
        """Add test entries."""
        history = self.query_one("#history", HistoryLog)

        # Add test entries
        history.add_entry("First test entry")
        history.add_entry("Second test entry with more text")
        history.add_entry("Third entry - click to expand!")

        self.notify("Added 3 test entries", severity="information")


if __name__ == "__main__":
    SimpleHistoryTest().run()
