"""Test script for ASCII rendering - All states without interaction."""

import sys
from datetime import datetime
from voice_tui.ascii_app import VoiceToTextASCIIApp
from voice_tui.config import Config


class MockController:
    """Mock controller for testing."""
    pass


def print_separator():
    """Print separator between tests."""
    print("\n" + "=" * 90 + "\n")


def test_idle_state():
    """Test idle state rendering."""
    print("IDLE STATE")
    print_separator()

    config = Config.load(None)
    app = VoiceToTextASCIIApp(config, MockController())

    app.current_status = "idle"
    app._render_frame()
    print_separator()


def test_recording_state():
    """Test recording state rendering."""
    print("RECORDING STATE")
    print_separator()

    config = Config.load(None)
    app = VoiceToTextASCIIApp(config, MockController())

    # Set recording state
    app.current_status = "recording"
    app.recording_duration = 3.45
    app.audio_level = 0.45
    app.peak_level = 0.87

    # Add some waveform data
    for i in range(80):
        level = 0.3 + (i % 10) / 20.0  # Varying levels
        app.waveform.update(level)

    app._render_frame()
    print_separator()


def test_processing_state():
    """Test processing state rendering."""
    print("PROCESSING STATE")
    print_separator()

    config = Config.load(None)
    app = VoiceToTextASCIIApp(config, MockController())

    app.current_status = "processing"
    app.status_message = "Transcribing..."

    app._render_frame()
    print_separator()


def test_complete_state():
    """Test complete state with history."""
    print("COMPLETE STATE WITH HISTORY")
    print_separator()

    config = Config.load(None)
    app = VoiceToTextASCIIApp(config, MockController())

    # Add history entries
    app.history.add_entry(datetime.now(), "This is a test transcription that demonstrates the history display.")
    app.history.add_entry(datetime.now(), "Another entry showing multiple transcriptions.")
    app.history.add_entry(datetime.now(), "Short text.")
    app.history.add_entry(
        datetime.now(),
        "This is a very long transcription that will be truncated to fit the available width in the display panel."
    )

    app.current_status = "complete"
    app.status_message = "Transcription complete"

    app._render_frame()
    print_separator()


def test_error_state():
    """Test error state rendering."""
    print("ERROR STATE")
    print_separator()

    config = Config.load(None)
    app = VoiceToTextASCIIApp(config, MockController())

    app.current_status = "error"
    app.status_message = "Recording failed: No microphone detected"

    app._render_frame()
    print_separator()


def main():
    """Run all tests."""
    print("\n" + "=" * 90)
    print("ASCII RENDERING TEST SUITE - ALL STATES")
    print("=" * 90 + "\n")

    test_idle_state()
    test_recording_state()
    test_processing_state()
    test_complete_state()
    test_error_state()

    print("All tests complete!")


if __name__ == "__main__":
    main()
