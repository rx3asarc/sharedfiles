"""Test the new collapsible history log feature."""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static
from voice_tui.ui.history_log import HistoryLog


class HistoryTestApp(App):
    """Test app for the collapsible history log."""

    CSS = """
    Screen {
        background: #0f172a;
    }

    #main {
        padding: 2;
        height: 100%;
    }

    #history-section {
        height: 1fr;
        width: 100%;
        border: solid #3b82f6;
        padding: 1;
    }

    #history-title {
        color: #f8fafc;
        text-style: bold;
        margin-bottom: 1;
    }

    HistoryLog {
        height: 100%;
        width: 100%;
        background: #1e293b;
        border: solid #334155;
    }

    /* History Entry Styles */
    .history-entry {
        height: auto;
        width: 100%;
        padding: 0;
        margin: 0;
        background: #1e293b;
        border-bottom: solid #334155;
    }

    .history-entry:hover {
        background: #334155;
    }

    .entry-header {
        height: auto;
        width: 100%;
        padding: 1;
        layout: horizontal;
        align: left middle;
    }

    .toggle-button {
        width: 3;
        min-width: 3;
        height: 1;
        padding: 0;
        margin: 0 1 0 0;
        border: none;
        background: transparent;
        color: #94a3b8;
    }

    .toggle-button:hover {
        background: #3b82f6 20%;
        color: #3b82f6;
    }

    .entry-preview {
        width: 1fr;
        height: auto;
        padding: 0;
        margin: 0;
        color: #f8fafc;
    }

    .copy-button {
        width: 4;
        min-width: 4;
        height: 1;
        padding: 0;
        margin: 0 0 0 1;
        border: none;
        background: transparent;
    }

    .copy-button:hover {
        background: #10b981 20%;
    }

    .entry-full-text {
        width: 100%;
        height: auto;
        padding: 1 2 1 5;
        margin: 0;
        background: #0f172a;
        color: #f8fafc;
        border-top: solid #334155;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("a", "add_entry", "Add Test Entry"),
        ("c", "clear", "Clear History"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the test app."""
        yield Header()

        with Container(id="main"):
            with Vertical(id="history-section"):
                yield Static("Transcription History (Press 'a' to add test entries)", id="history-title")
                yield HistoryLog(id="history-log")

        yield Footer()

    def on_mount(self) -> None:
        """Add some sample entries on mount."""
        history_log = self.query_one("#history-log", HistoryLog)

        # Add sample entries showing different use cases
        sample_texts = [
            "This is a short test transcription.",
            "This is a much longer transcription that will be truncated in the preview. It contains multiple sentences and demonstrates how the collapsible history entries work when the text is very long. You can click the arrow button on the left to expand and see the full text, or click anywhere on the entry to toggle expansion.",
            "Quick note: Buy milk and eggs from the store.",
            "Meeting notes: Discussed the new feature implementation with the team. Everyone agreed on the timeline and priorities. Next steps include creating a detailed specification document, assigning tasks to team members, and scheduling a follow-up meeting for next week to review progress.",
            "Reminder: Call doctor tomorrow at 2 PM to schedule appointment.",
            "Email draft: Hey team, just wanted to follow up on our discussion from earlier today. I think we made great progress on identifying the key requirements for the new collapsible history feature. Looking forward to seeing this implemented!",
            "Code review notes: The implementation looks solid. Minor suggestions: add keyboard shortcuts, improve hover states, and consider adding a search filter for longer histories.",
        ]

        for text in reversed(sample_texts):  # Reverse so newest appears first
            history_log.add_entry(text)

        self.notify("Click any entry to expand/collapse. Press 'a' to add more entries.", timeout=5)

    def action_add_entry(self) -> None:
        """Add a test entry."""
        import random
        texts = [
            "This is a new test entry added dynamically.",
            "Another transcription example with some more text to show the preview truncation feature.",
            "Quick test: The collapsible feature is working!",
        ]
        history_log = self.query_one("#history-log", HistoryLog)
        history_log.add_entry(random.choice(texts))
        self.notify("Added new test entry", severity="information")

    def action_clear(self) -> None:
        """Clear history."""
        history_log = self.query_one("#history-log", HistoryLog)
        history_log.clear_history()
        self.notify("History cleared", severity="information")


if __name__ == "__main__":
    app = HistoryTestApp()
    app.run()
