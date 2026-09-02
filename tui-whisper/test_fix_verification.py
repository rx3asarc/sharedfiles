"""Test to verify history entry fixes."""

from textual.app import App
from textual.widgets import Header, Footer, Static
from textual.containers import Container, Vertical
from voice_tui.ui.history_log import HistoryLog


class HistoryFixTest(App):
    """Test app to verify history entries display correctly."""

    CSS = """
    Screen {
        background: #0f172a;
    }

    #main {
        height: 100%;
        padding: 1;
    }

    #test-info {
        height: auto;
        padding: 1;
        background: #1e293b;
        color: #10b981;
        text-align: center;
        margin-bottom: 1;
    }

    #history-container {
        height: 1fr;
        border: thick #3b82f6;
        padding: 1;
    }

    HistoryLog {
        height: 100%;
        width: 100%;
        background: #1e293b;
    }

    /* Include all history entry styles */
    .history-entry {
        height: auto;
        min-height: 3;
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
        min-height: 3;
        width: 100%;
        padding: 1;
        layout: horizontal;
        align: left middle;
    }

    .toggle-button {
        width: 3;
        min-width: 3;
        height: 3;
        min-height: 1;
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
        height: 3;
        min-height: 1;
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

    .history-placeholder {
        width: 100%;
        height: auto;
        padding: 2;
        text-align: center;
        color: #64748b;
        text-style: dim italic;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("a", "add_entry", "Add Entry"),
        ("c", "clear", "Clear"),
    ]

    def compose(self):
        yield Header()

        with Vertical(id="main"):
            yield Static(
                "HISTORY FIX VERIFICATION TEST\n"
                "Press 'a' to add entries | 'c' to clear | 'q' to quit\n"
                "Click entries to expand/collapse",
                id="test-info"
            )

            with Container(id="history-container"):
                yield HistoryLog(id="history")

        yield Footer()

    def on_mount(self):
        """Add initial test entries."""
        self.add_test_entries()

    def add_test_entries(self):
        """Add several test entries."""
        history = self.query_one("#history", HistoryLog)

        test_data = [
            "Short entry",
            "This is a medium length entry that should display properly with the new fixes applied.",
            "This is a very long entry that will definitely be truncated in the preview and will require clicking the expand arrow to see the full text. It contains multiple sentences to really test the collapsible functionality and ensure everything works as expected.",
        ]

        for text in test_data:
            history.add_entry(text)

        self.notify(f"Added {len(test_data)} test entries", severity="information")

    def action_add_entry(self):
        """Add a new test entry."""
        import random
        history = self.query_one("#history", HistoryLog)

        entries = [
            "New test entry added dynamically",
            "Another entry to test the scrolling and display",
            "Testing testing one two three",
        ]

        text = random.choice(entries)
        history.add_entry(text)
        self.notify("Entry added!", severity="information")

    def action_clear(self):
        """Clear all entries."""
        history = self.query_one("#history", HistoryLog)
        history.clear_history()
        self.notify("History cleared", severity="information")


if __name__ == "__main__":
    HistoryFixTest().run()
