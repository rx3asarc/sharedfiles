"""Ultra-simple test to see if ANYTHING renders."""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Label
from textual.containers import Container, Vertical


class SimpleTestApp(App):
    """Simplest possible app to test rendering."""

    CSS = """
    Screen {
        background: black;
    }

    #test-box {
        width: 80%;
        height: 10;
        border: heavy green;
        background: blue;
        padding: 2;
        margin: 2;
        color: white;
    }

    #test-text {
        color: yellow;
        text-style: bold;
        height: 3;
        content-align: center middle;
    }

    #history-test {
        height: 10;
        width: 80%;
        border: solid red;
        background: purple;
        color: white;
        padding: 1;
        margin: 2;
    }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        """Compose with very simple widgets."""
        yield Header(show_clock=True)

        # Test status box
        with Container(id="test-box"):
            yield Static("STATUS PANEL TEST - YOU SHOULD SEE THIS!", id="test-text")

        # Test history
        with Container(id="history-test"):
            yield Static("HISTORY SECTION TEST - YOU SHOULD SEE THIS TOO!")
            yield Static("Line 1 of history")
            yield Static("Line 2 of history")
            yield Static("Line 3 of history")

        yield Footer()


if __name__ == "__main__":
    app = SimpleTestApp()
    app.run()
