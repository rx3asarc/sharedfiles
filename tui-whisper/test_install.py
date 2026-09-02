"""Simple test script to verify installation and dependencies."""

import sys


def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    errors = []

    # Test core dependencies
    modules = [
        ('numpy', 'numpy'),
        ('sounddevice', 'sounddevice'),
        ('faster_whisper', 'faster-whisper'),
        ('keyboard', 'keyboard'),
        ('pyperclip', 'pyperclip'),
        ('textual', 'textual'),
        ('yaml', 'PyYAML'),
    ]

    for module_name, package_name in modules:
        try:
            __import__(module_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name} (MISSING)")
            errors.append(package_name)

    return errors


def test_microphone():
    """Test microphone availability."""
    print("\nTesting microphone...")
    try:
        import sounddevice as sd
        device_info = sd.query_devices(kind='input')
        print(f"  ✓ Microphone detected: {device_info['name']}")
        return True
    except Exception as e:
        print(f"  ✗ Microphone error: {e}")
        return False


def test_voice_tui():
    """Test that voice_tui package can be imported."""
    print("\nTesting voice_tui package...")
    try:
        from voice_tui import __version__
        from voice_tui.config import Config
        from voice_tui.recorder import AudioRecorder
        from voice_tui.transcriber import WhisperTranscriber
        from voice_tui.ui import VoiceToTextApp
        print(f"  ✓ voice_tui v{__version__}")
        print(f"  ✓ All modules importable")
        return True
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Voice-to-Text TUI Installation Test")
    print("=" * 60)

    # Test imports
    missing = test_imports()

    # Test microphone
    mic_ok = test_microphone()

    # Test voice_tui package
    package_ok = test_voice_tui()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    if missing:
        print(f"✗ Missing dependencies: {', '.join(missing)}")
        print("\nTo install missing dependencies:")
        print("  pip install -r requirements.txt")
        return False

    if not mic_ok:
        print("⚠ Microphone not detected or not accessible")
        print("  The app will not work without a microphone.")
        print("  Check your system settings and try again.")

    if not package_ok:
        print("✗ voice_tui package not properly installed")
        print("\nTo install:")
        print("  pip install -e .")
        return False

    print("✓ All tests passed!")
    print("\nYou're ready to use voice-tui!")
    print("\nRun with: voice-tui")
    print("Or: python -m voice_tui.main")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
