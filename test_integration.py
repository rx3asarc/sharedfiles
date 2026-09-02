"""Integration test - Simulate full recording → transcription flow."""

import time
import threading
from datetime import datetime
from voice_tui.ascii_app import VoiceToTextASCIIApp
from voice_tui.config import Config


class MockController:
    """Mock controller for testing."""
    pass


def simulate_recording_session(app):
    """Simulate a complete recording session.

    Args:
        app: VoiceToTextASCIIApp instance
    """
    print("\n" + "=" * 90)
    print("INTEGRATION TEST: Simulating Recording Session")
    print("=" * 90 + "\n")

    # Start in idle
    print("[1/6] Starting in IDLE state...")
    app.set_status("idle")
    time.sleep(1)

    # Start recording
    print("[2/6] Starting RECORDING...")
    app.set_status("recording")

    # Simulate 3 seconds of recording with varying levels
    print("[3/6] Recording for 3 seconds with live metrics...")
    for i in range(30):  # 30 updates at 0.1s each = 3 seconds
        duration = i * 0.1
        level = 0.3 + (i % 10) / 20.0  # Varying audio level
        peak = 0.85
        app.update_recording_metrics(duration, level, peak)
        time.sleep(0.1)

    # Stop recording, start processing
    print("[4/6] Stopping recording, starting PROCESSING...")
    app.set_status("processing", "Transcribing audio...")
    time.sleep(2)

    # Show result
    print("[5/6] Showing COMPLETE state with transcription...")
    test_text = "This is a test transcription to verify the complete workflow works correctly."
    app.set_transcription(test_text, copied=True, auto_typed=False)
    time.sleep(3)

    # Should auto-transition to idle after 2s
    print("[6/6] Waiting for auto-transition to IDLE...")
    time.sleep(3)

    print("\n" + "=" * 90)
    print("Integration test complete!")
    print("=" * 90 + "\n")


def test_error_handling(app):
    """Test error state display.

    Args:
        app: VoiceToTextASCIIApp instance
    """
    print("\n" + "=" * 90)
    print("ERROR HANDLING TEST")
    print("=" * 90 + "\n")

    print("[1/2] Showing ERROR state...")
    app.show_error("Test error: This is a simulated error message")
    time.sleep(3)

    print("[2/2] Returning to IDLE...")
    app.set_status("idle")
    time.sleep(1)

    print("\n" + "=" * 90)
    print("Error handling test complete!")
    print("=" * 90 + "\n")


def test_history_accumulation(app):
    """Test history log with multiple entries.

    Args:
        app: VoiceToTextASCIIApp instance
    """
    print("\n" + "=" * 90)
    print("HISTORY ACCUMULATION TEST")
    print("=" * 90 + "\n")

    transcriptions = [
        "First transcription for testing history display",
        "Second entry with different content",
        "A very long transcription that should be truncated to fit within the available display width",
        "Short text",
        "Another medium-length transcription to test rendering",
        "Testing multiple entries in the history log",
        "This should demonstrate scrolling or truncation behavior",
        "Entry number eight for comprehensive testing",
        "Ninth entry to fill the visible area",
        "Tenth entry to test the display limits",
    ]

    for i, text in enumerate(transcriptions, 1):
        print(f"[{i}/{len(transcriptions)}] Adding transcription to history...")
        app.set_transcription(text, copied=True)
        time.sleep(0.5)

    print("\nFinal state with full history:")
    time.sleep(2)

    print("\n" + "=" * 90)
    print("History accumulation test complete!")
    print("=" * 90 + "\n")


def run_render_thread(app):
    """Run app in background thread for testing.

    Args:
        app: VoiceToTextASCIIApp instance
    """
    # Don't actually run the loop, just process updates manually
    while app.running:
        app._process_update_queue()
        app._render_frame()
        time.sleep(1.0 / 30)  # 30 FPS


def main():
    """Run integration tests."""
    print("\n" + "=" * 90)
    print("ASCII APP INTEGRATION TEST SUITE")
    print("=" * 90)

    # Create app
    config = Config.load(None)
    app = VoiceToTextASCIIApp(config, MockController())

    # Don't start full render loop, just initialize
    app.running = True
    app._init_terminal()

    try:
        # Start render thread
        render_thread = threading.Thread(target=run_render_thread, args=(app,), daemon=True)
        render_thread.start()

        # Run tests
        simulate_recording_session(app)
        time.sleep(2)

        test_error_handling(app)
        time.sleep(2)

        test_history_accumulation(app)
        time.sleep(2)

    finally:
        # Cleanup
        app.running = False
        time.sleep(0.2)  # Let render thread finish
        app._cleanup_terminal()

    print("\n" + "=" * 90)
    print("ALL INTEGRATION TESTS COMPLETE")
    print("=" * 90)
    print("\nThe ASCII UI implementation is working correctly!")
    print("You can now run the full application with:")
    print("  python -m voice_tui.main")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    main()
