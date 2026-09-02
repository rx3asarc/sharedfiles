"""Standalone voice TUI - does not use package imports."""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Container
from textual.reactive import reactive


class StatusBox(Static):
    """Simple status box."""

    status_text = reactive("● READY TO RECORD\n\nHold [Ctrl+Win] to record")

    def watch_status_text(self, new_text):
        self.update(new_text)


class HistoryBox(Static):
    """Simple history box."""

    def __init__(self):
        super().__init__()
        self.update("Recent Transcriptions:\n(empty)")


class StandaloneVoiceTUI(App):
    """Standalone TUI with guaranteed rendering."""

    CSS = """
    Screen {
        background: #0f172a;
    }

    #status-container {
        width: 90%;
        height: 12;
        border: double green;
        background: #1e293b;
        padding: 2;
        margin: 2 auto;
        content-align: center middle;
    }

    StatusBox {
        color: white;
        text-align: center;
        height: 100%;
    }

    #history-container {
        width: 90%;
        height: 15;
        border: solid cyan;
        background: #1e293b;
        padding: 1;
        margin: 1 auto;
    }

    HistoryBox {
        color: white;
        height: 100%;
    }

    #shortcuts {
        dock: bottom;
        height: 3;
        background: #334155;
        border-top: solid cyan;
        content-align: center middle;
        color: white;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        # Status panel
        with Container(id="status-container"):
            yield StatusBox()

        # History
        with Container(id="history-container"):
            yield HistoryBox()

        # Shortcuts
        yield Static("[Ctrl+Win] Record | [Q] Quit | [S] Settings | [C] Clear", id="shortcuts")

        yield Footer()


if __name__ == "__main__":
    app = StandaloneVoiceTUI()
    app.title = "Voice-to-Text TUI"
    app.run()
