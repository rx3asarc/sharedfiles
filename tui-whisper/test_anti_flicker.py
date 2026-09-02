"""Test anti-flicker improvements - Simulate recording with frequent updates."""

import time
import random
from voice_tui.ascii_app import VoiceToTextASCIIApp
from voice_tui.config import Config


class MockController:
    """Mock controller for testing."""
    pass


def test_recording_flicker():
    """Simulate recording with frequent metric updates."""
    print("Testing anti-flicker during recording...")
    print("This simulates the recording state with metric updates.")
    print()

    config = Config.load(None)
    app = VoiceToTextASCIIApp(config, MockController())

    # Initialize terminal
    app._init_terminal()

    try:
        # Set to recording state
        app.set_status("recording")

        # Simulate 5 seconds of recording
        start_time = time.time()
        duration = 0.0
        update_count = 0
        render_count = 0

        print("Recording for 5 seconds...")
        print("Watch for flickering - there should be MINIMAL updates")
        print()

        while duration < 5.0:
            current_time = time.time()
            duration = current_time - start_time

            # Simulate audio level (fluctuating)
            level = 0.3 + random.random() * 0.4  # 30-70%
            peak = 0.85

            # Send update (this happens 10 times per second in real app)
            app.update_recording_metrics(duration, level, peak)
            update_count += 1

            # Process queue and render if needed
            app._process_update_queue()

            # Check if render is needed
            if app.needs_render:
                app._render_frame()
                app.needs_render = False
                render_count += 1

            # Sleep to simulate real-time updates (10 updates/sec)
            time.sleep(0.1)

        print()
        print(f"Test complete!")
        print(f"  Updates sent: {update_count}")
        print(f"  Renders performed: {render_count}")
        print(f"  Render reduction: {100 * (1 - render_count/update_count):.1f}%")
        print()

        if render_count < update_count * 0.5:
            print("[OK] Anti-flicker working - renders significantly reduced!")
        else:
            print("[WARNING] Too many renders - flickering may still occur")

        time.sleep(2)

    finally:
        app._cleanup_terminal()

    print()
    print("Test finished!")


def test_change_detection():
    """Test that small changes don't trigger renders."""
    print("=" * 80)
    print("CHANGE DETECTION TEST")
    print("=" * 80)
    print()

    config = Config.load(None)
    app = VoiceToTextASCIIApp(config, MockController())

    # Test 1: Same value multiple times
    print("Test 1: Sending same metrics 10 times...")
    render_triggered = 0
    for i in range(10):
        app.update_recording_metrics(1.0, 0.5, 0.8)
        app._process_update_queue()
        if app.needs_render:
            render_triggered += 1
            app.needs_render = False

    print(f"  Renders triggered: {render_triggered}/10")
    if render_triggered <= 1:
        print("  [OK] No redundant renders")
    else:
        print("  [WARNING] Too many renders for same value")
    print()

    # Test 2: Small changes below threshold
    print("Test 2: Sending small changes (below 2% threshold)...")
    render_triggered = 0
    for i in range(10):
        level = 0.500 + i * 0.001  # 0.1% increments
        app.update_recording_metrics(1.0, level, 0.8)
        app._process_update_queue()
        if app.needs_render:
            render_triggered += 1
            app.needs_render = False

    print(f"  Renders triggered: {render_triggered}/10")
    if render_triggered <= 2:
        print("  [OK] Small changes ignored")
    else:
        print("  [WARNING] Too sensitive to small changes")
    print()

    # Test 3: Significant changes
    print("Test 3: Sending significant changes (above 2% threshold)...")
    render_triggered = 0
    for i in range(10):
        level = 0.5 + i * 0.05  # 5% increments
        app.update_recording_metrics(1.0, level, 0.8)
        app._process_update_queue()
        if app.needs_render:
            render_triggered += 1
            app.needs_render = False

    print(f"  Renders triggered: {render_triggered}/10")
    if render_triggered >= 8:
        print("  [OK] Significant changes detected")
    else:
        print("  [WARNING] Missing significant changes")
    print()

    print("=" * 80)


def main():
    """Run anti-flicker tests."""
    print()
    print("=" * 80)
    print("ANTI-FLICKER TEST SUITE")
    print("=" * 80)
    print()

    test_change_detection()
    test_recording_flicker()

    print()
    print("=" * 80)
    print("All anti-flicker tests complete!")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
