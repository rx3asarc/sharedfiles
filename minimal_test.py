"""Absolute minimal working TUI - no custom widgets."""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Vertical

class MinimalApp(App):
    """Minimal app with NO custom widgets."""

    CSS = """
    Screen {
        background: #0f172a;
    }

    #big-box {
        width: 80%;
        height: 10;
        border: double green;
        background: blue;
        content-align: center middle;
        margin: 2;
    }

    #history-box {
        width: 90%;
        height: 12;
        border: solid cyan;
        background: purple;
        margin: 1;
        padding: 1;
    }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        """Directly yield widgets - NO MainScreen."""
        yield Header(show_clock=True)

        with Vertical():
            yield Static("● READY TO RECORD\n\nHold [Ctrl+Win] to record", id="big-box")
            yield Static("Recent Transcriptions:\n(No transcriptions yet)", id="history-box")

        yield Footer()


if __name__ == "__main__":
    app = MinimalApp()
    app.title = "Minimal Test"
    app.run()
