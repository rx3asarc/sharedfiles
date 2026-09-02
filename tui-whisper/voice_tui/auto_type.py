"""Auto-type functionality for pasting text at cursor position."""

import time
import threading
from typing import Optional

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    pyautogui = None


class AutoTyper:
    """Handles automatic typing of text at cursor position using PyAutoGUI."""

    def __init__(self, type_interval: float = 0.01):
        """Initialize the auto-typer.

        Args:
            type_interval: Seconds between keystrokes for natural typing feel.
        """
        self.type_interval = type_interval
        self._is_typing = False
        self._stop_typing = False

        if not PYAUTOGUI_AVAILABLE:
            print("Warning: PyAutoGUI not available. Auto-type functionality disabled.")

        # Configure PyAutoGUI settings
        if PYAUTOGUI_AVAILABLE and pyautogui:
            pyautogui.FAILSAFE = True  # Move mouse to corner to abort
            pyautogui.PAUSE = self.type_interval

    def type_text(self, text: str, paste_fallback: bool = True) -> bool:
        """Type text character by character at current cursor position.

        Args:
            text: Text to type
            paste_fallback: If True, use clipboard paste for long text (>50 chars)

        Returns:
            True if typing succeeded, False otherwise.
        """
        if not PYAUTOGUI_AVAILABLE or not pyautogui:
            print("PyAutoGUI not available - cannot auto-type")
            return False

        if not text or not text.strip():
            return True  # Nothing to type

        # For long text, use paste method for speed
        if paste_fallback and len(text) > 50:
            return self._paste_text(text)

        try:
            self._is_typing = True
            self._stop_typing = False

            # Small delay to ensure focus is set
            time.sleep(0.1)

            for char in text:
                if self._stop_typing:
                    break

                # Handle special characters
                if char == '\n':
                    pyautogui.press('enter')
                elif char == '\t':
                    pyautogui.press('tab')
                else:
                    pyautogui.write(char)

            self._is_typing = False
            return True

        except Exception as e:
            print(f"Auto-type error: {e}")
            self._is_typing = False
            return False

    def _paste_text(self, text: str) -> bool:
        """Paste text using clipboard (Ctrl+V).

        Args:
            text: Text to paste

        Returns:
            True if pasting succeeded, False otherwise.
        """
        try:
            # Store current clipboard content
            try:
                import pyperclip
                old_clipboard = pyperclip.paste()
            except:
                old_clipboard = None

            # Set new text to clipboard
            try:
                import pyperclip
                pyperclip.copy(text)
            except Exception as e:
                print(f"Failed to copy to clipboard: {e}")
                return False

            # Paste
            time.sleep(0.1)  # Small delay
            pyautogui.hotkey('ctrl', 'v')

            # Restore original clipboard content
            if old_clipboard is not None:
                try:
                    import pyperclip
                    time.sleep(0.2)  # Wait for paste to complete
                    pyperclip.copy(old_clipboard)
                except:
                    pass

            return True

        except Exception as e:
            print(f"Paste error: {e}")
            return False

    def type_text_async(self, text: str, callback: Optional[callable] = None) -> None:
        """Type text in a background thread.

        Args:
            text: Text to type
            callback: Optional callback function called with success status
        """
        def type_worker():
            success = self.type_text(text)
            if callback:
                callback(success)

        threading.Thread(target=type_worker, daemon=True).start()

    def stop_typing(self) -> None:
        """Stop current typing operation."""
        self._stop_typing = True

    @property
    def is_typing(self) -> bool:
        """Check if currently typing."""
        return self._is_typing

    @property
    def is_available(self) -> bool:
        """Check if auto-type functionality is available."""
        return PYAUTOGUI_AVAILABLE


def test_auto_type() -> None:
    """Test auto-type functionality."""
    if not PYAUTOGUI_AVAILABLE:
        print("PyAutoGUI not available - cannot test auto-type")
        return

    typer = AutoTyper()

    print("Testing auto-type functionality...")
    print("Click in any text field (notepad, browser, etc.) within 5 seconds")
    print("The test will type 'Hello, World!'")

    time.sleep(5)

    success = typer.type_text("Hello, World!")
    if success:
        print("Auto-type test completed successfully!")
    else:
        print("Auto-type test failed!")


if __name__ == "__main__":
    test_auto_type()