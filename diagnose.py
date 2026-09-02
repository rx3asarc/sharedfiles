"""Diagnostic script to check what's being loaded."""

import sys
print("=" * 60)
print("DIAGNOSTICS - Voice TUI")
print("=" * 60)

# Check imports
print("\n1. Checking imports...")
try:
    from voice_tui.app import VoiceToTextApp
    print("   [OK] VoiceToTextApp imported from app.py")
except Exception as e:
    print(f"   [FAIL] Failed to import VoiceToTextApp: {e}")
    sys.exit(1)

try:
    from voice_tui.ui import MainScreen, StatusPanel, HistoryLog
    print("   [OK] UI components imported")
except Exception as e:
    print(f"   [FAIL] Failed to import UI components: {e}")
    sys.exit(1)

# Check CSS path
print("\n2. Checking CSS file...")
from pathlib import Path
css_path = Path(__file__).parent / "voice_tui" / "ui" / "styles.tcss"
if css_path.exists():
    print(f"   [OK] CSS file exists: {css_path}")
    with open(css_path) as f:
        lines = len(f.readlines())
    print(f"   [OK] CSS file has {lines} lines")
else:
    print(f"   [FAIL] CSS file NOT found: {css_path}")

# Check what widgets are in MainScreen
print("\n3. Checking MainScreen composition...")
from voice_tui.ui.main_screen import MainScreen
import inspect
source = inspect.getsource(MainScreen.compose)
if "StatusPanel" in source:
    print("   [OK] MainScreen includes StatusPanel")
if "HistoryLog" in source:
    print("   [OK] MainScreen includes HistoryLog")
if "MetricsRow" in source:
    print("   [OK] MainScreen includes MetricsRow")
if "shortcuts-bar" in source:
    print("   [OK] MainScreen includes shortcuts bar")

# Try to create the app
print("\n4. Creating app instance...")
try:
    from voice_tui.config import Config
    config = Config()
    app = VoiceToTextApp(config=config, controller=None)
    print(f"   [OK] App created successfully")
    print(f"   [OK] App title: {app.title}")
    print(f"   [OK] App CSS path: {app.CSS_PATH}")
except Exception as e:
    print(f"   [FAIL] Failed to create app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Try to compose the layout
print("\n5. Testing layout composition...")
try:
    from textual.app import App

    class TestApp(App):
        def compose(self):
            from voice_tui.ui.main_screen import MainScreen
            yield MainScreen()

    test_app = TestApp()
    print("   [OK] Layout can be composed")
except Exception as e:
    print(f"   [FAIL] Failed to compose layout: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("DIAGNOSTICS COMPLETE")
print("=" * 60)
print("\nIf all checks passed, try running:")
print("  voice-tui")
print("\nOr run the demo:")
print("  python demo_ui.py")
