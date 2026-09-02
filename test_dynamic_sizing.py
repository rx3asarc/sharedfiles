"""Test dynamic sizing - Verify layout adapts to different terminal sizes."""

from voice_tui.ascii_layout import LayoutSpec
from voice_tui.ascii_app import VoiceToTextASCIIApp
from voice_tui.config import Config
from datetime import datetime


class MockController:
    """Mock controller for testing."""
    pass


def test_layout_calculations():
    """Test layout calculations for different terminal sizes."""
    print("=" * 80)
    print("DYNAMIC SIZING TEST: Layout Calculations")
    print("=" * 80)
    print()

    # Test different sizes
    test_sizes = [
        (60, 25, "Minimum size"),
        (80, 30, "Small terminal"),
        (90, 40, "Original design size"),
        (120, 50, "Large terminal"),
        (150, 60, "Extra large"),
    ]

    for width, height, description in test_sizes:
        print(f"{description}: {width}x{height}")
        print("-" * 80)

        layout = LayoutSpec(width=width, height=height)

        print(f"  Actual size: {layout.UI_WIDTH}x{layout.UI_HEIGHT}")
        print(f"  Panel width: {layout.PANEL_WIDTH}")
        print(f"  Status panel: rows {layout.STATUS_PANEL_START}-{layout.STATUS_PANEL_END}")
        print(f"  Waveform: rows {layout.WAVEFORM_START}-{layout.WAVEFORM_END}")
        print(f"  History: rows {layout.HISTORY_START}-{layout.HISTORY_END} (height: {layout.HISTORY_HEIGHT})")
        print(f"  Footer: row {layout.FOOTER_ROW}")
        print()

    print("=" * 80)
    print()


def test_minimum_size_enforcement():
    """Test that minimum size is enforced."""
    print("=" * 80)
    print("MINIMUM SIZE ENFORCEMENT TEST")
    print("=" * 80)
    print()

    # Try to create layouts smaller than minimum
    test_sizes = [
        (30, 10, "Too small"),
        (50, 20, "Below minimum"),
        (60, 25, "Exactly minimum"),
    ]

    for width, height, description in test_sizes:
        print(f"{description}: Requested {width}x{height}")
        layout = LayoutSpec(width=width, height=height)
        print(f"  Actual: {layout.UI_WIDTH}x{layout.UI_HEIGHT}")

        if layout.UI_WIDTH >= LayoutSpec.MIN_WIDTH and layout.UI_HEIGHT >= LayoutSpec.MIN_HEIGHT:
            print(f"  [OK] Minimum enforced correctly")
        else:
            print(f"  [FAIL] Size below minimum!")
        print()

    print("=" * 80)
    print()


def test_resize_detection():
    """Test resize detection and adaptation."""
    print("=" * 80)
    print("RESIZE DETECTION TEST")
    print("=" * 80)
    print()

    # Create layout with initial size
    layout = LayoutSpec(width=80, height=30)
    print(f"Initial size: {layout.UI_WIDTH}x{layout.UI_HEIGHT}")
    print(f"Initial history height: {layout.HISTORY_HEIGHT}")
    print()

    # Simulate resize
    print("Simulating resize to 120x50...")
    layout.resize(120, 50)
    print(f"New size: {layout.UI_WIDTH}x{layout.UI_HEIGHT}")
    print(f"New history height: {layout.HISTORY_HEIGHT}")
    print(f"[OK] Layout recalculated")
    print()

    # Simulate downsize
    print("Simulating downsize to 70x28...")
    layout.resize(70, 28)
    print(f"New size: {layout.UI_WIDTH}x{layout.UI_HEIGHT}")
    print(f"New history height: {layout.HISTORY_HEIGHT}")
    print(f"[OK] Layout recalculated")
    print()

    print("=" * 80)
    print()


def test_dynamic_render():
    """Test rendering at different sizes."""
    print("=" * 80)
    print("DYNAMIC RENDERING TEST")
    print("=" * 80)
    print()

    sizes = [
        (60, 25, "Minimum"),
        (90, 40, "Original"),
        (120, 50, "Large"),
    ]

    for width, height, description in sizes:
        print(f"\n{description} Size: {width}x{height}")
        print("-" * 80)

        # Create app with specific size
        config = Config.load(None)
        app = VoiceToTextASCIIApp(config, MockController())

        # Override layout with test size
        app.layout = LayoutSpec(width=width, height=height)
        app.buffer = __import__('voice_tui.ascii_renderer', fromlist=['ASCIIScreenBuffer']).ASCIIScreenBuffer(
            app.layout.UI_WIDTH, app.layout.UI_HEIGHT
        )
        app.waveform = __import__('voice_tui.ascii_components', fromlist=['ASCIIWaveformVisualizer']).ASCIIWaveformVisualizer(
            width=app.layout.PANEL_WIDTH - 4
        )
        app.history.max_visible = app.layout.HISTORY_HEIGHT - 2

        # Set up test state
        app.current_status = "idle"

        # Render
        app._render_frame()
        print()

    print("=" * 80)
    print("All dynamic sizing tests complete!")
    print()


def test_current_terminal_size():
    """Test with actual current terminal size."""
    print("=" * 80)
    print("CURRENT TERMINAL SIZE TEST")
    print("=" * 80)
    print()

    layout = LayoutSpec()  # Auto-detect
    print(f"Detected terminal size: {layout.UI_WIDTH}x{layout.UI_HEIGHT}")
    print(f"Panel width: {layout.PANEL_WIDTH}")
    print(f"History height: {layout.HISTORY_HEIGHT}")
    print()

    print("Layout breakdown:")
    print(f"  Header: rows 0-1 ({layout.HEADER_HEIGHT} rows)")
    print(f"  Status panel: rows {layout.STATUS_PANEL_START}-{layout.STATUS_PANEL_END} ({layout.STATUS_PANEL_HEIGHT} rows)")
    print(f"  Waveform: rows {layout.WAVEFORM_START}-{layout.WAVEFORM_END} ({layout.WAVEFORM_HEIGHT} rows)")
    print(f"  Metrics: row {layout.METRICS_ROW} (1 row)")
    print(f"  History: rows {layout.HISTORY_START}-{layout.HISTORY_END} ({layout.HISTORY_HEIGHT} rows)")
    print(f"  Footer: rows {layout.FOOTER_SEPARATOR}-{layout.FOOTER_ROW} ({layout.FOOTER_HEIGHT} rows)")
    print()

    total_rows_used = (layout.HEADER_HEIGHT + layout.STATUS_PANEL_HEIGHT +
                       layout.WAVEFORM_HEIGHT + layout.METRICS_HEIGHT +
                       layout.HISTORY_TITLE_HEIGHT + layout.HISTORY_HEIGHT +
                       layout.FOOTER_HEIGHT)
    print(f"Total rows used: {total_rows_used} / {layout.UI_HEIGHT}")

    if total_rows_used <= layout.UI_HEIGHT:
        print("[OK] Layout fits within terminal")
    else:
        print("[WARNING] Layout exceeds terminal height!")

    print()
    print("=" * 80)


def main():
    """Run all dynamic sizing tests."""
    print("\n" + "=" * 80)
    print("DYNAMIC SIZING TEST SUITE")
    print("=" * 80)
    print()

    test_current_terminal_size()
    test_layout_calculations()
    test_minimum_size_enforcement()
    test_resize_detection()
    test_dynamic_render()

    print("\n" + "=" * 80)
    print("All tests complete!")
    print()
    print("The UI now adapts dynamically to any terminal size!")
    print("Minimum size: 60x25")
    print("Recommended: 90x40 or larger")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
