"""ASCII-based Voice-to-Text TUI Application.

Replacement for Textual-based app.py with pure ASCII rendering.
Maintains same interface for controller compatibility.
"""

import sys
import time
import queue
import threading
from datetime import datetime
from typing import Optional

try:
    import keyboard
except ImportError:
    keyboard = None

from .ascii_renderer import ASCIIScreenBuffer
from .ascii_layout import LayoutSpec
from .ascii_components import (
    ASCIIStatusPanel,
    ASCIIWaveformVisualizer,
    ASCIIMetricsRow,
    ASCIIHistoryLog
)


class VoiceToTextASCIIApp:
    """ASCII-based TUI application for voice-to-text transcription.

    Maintains same interface as Textual VoiceToTextApp for controller compatibility.
    """

    def __init__(self, config, controller):
        """Initialize ASCII app.

        Args:
            config: Application configuration
            controller: Application controller instance
        """
        self.config = config
        self.controller = controller

        # Layout specification (dynamic, adapts to terminal size)
        self.layout = LayoutSpec()

        # Screen buffer
        self.buffer = ASCIIScreenBuffer(self.layout.UI_WIDTH, self.layout.UI_HEIGHT)

        # Components
        self.status_panel = ASCIIStatusPanel(hotkey=self.config.hotkey)
        # Waveform with attack/release smoothing (A): grows fast with voice,
        # settles slowly on pause - no jumpy expansion/contraction
        self.waveform = ASCIIWaveformVisualizer(
            width=self.layout.PANEL_WIDTH - 4,
            attack=0.5,
            release=0.07,
            field_height=self.layout.WAVEFORM_HEIGHT - 2
        )
        self.metrics = ASCIIMetricsRow()
        self.history = ASCIIHistoryLog(
            max_visible=self.layout.HISTORY_HEIGHT - 2,
            max_entries=100
        )

        # Application state
        self.current_status = "idle"
        self.recording_duration = 0.0
        self.audio_level = 0.0
        self.peak_level = 0.0
        self.status_message = ""

        # Previous state for change detection
        self.prev_duration = -1.0
        self.prev_level = -1.0
        self.prev_peak = -1.0

        # Thread-safe update queue
        self.update_queue = queue.Queue()
        self.running = False

        # Frame rate control (10 FPS is sufficient for text UI)
        self.target_fps = 10
        self.frame_time = 1.0 / self.target_fps

        # Resize detection
        self.last_resize_check = 0
        self.resize_check_interval = 1.0  # Check every second

        # Render control
        self.needs_render = True  # Force initial render

        # Add multiple test entries to verify history rendering
        test_time = datetime.now()
        self.history.add_entry(test_time, "Test 1: History rendering works if you see this!")
        self.history.add_entry(test_time, "Test 2: This is the second test entry.")
        self.history.add_entry(test_time, "Test 3: Multiple entries should appear here.")

        # Settings mode attributes
        self.settings_mode = False
        self.settings_cursor = 0
        self.settings_editing = False
        self.settings_edit_buffer = ""
        self.settings_edit_index = -1
        self.in_hotkey_capture = False
        self.settings_message = ""

        # Settings definitions: (display_name, attribute_name, type, [choices if type='choice'])
        self.settings_defs = [
            ("Model", "model_name", "choice", ["tiny", "base", "small", "medium", "large-v2", "large-v3"]),
            ("Language", "language", "string", None),
            ("Hotkey", "hotkey", "string", None),
            ("Sample Rate", "sample_rate", "int", None),
            ("Min Recording Duration", "min_recording_duration", "float", None),
            ("Device Type", "device_type", "choice", ["auto", "cpu", "cuda"]),
            ("Compute Type", "compute_type", "choice", ["auto", "int8", "float16", "float32"]),
            ("Auto Type", "auto_type", "bool", None),
            ("Auto Paste", "auto_paste", "bool", None),
            ("Type Interval", "type_interval", "float", None),
            ("Smart Formatting", "use_smart_formatting", "bool", None),
            ("OpenRouter API Key", "openrouter_api_key", "string", None),
            ("OpenRouter Model", "openrouter_model", "string", None),
        ]

    def run(self):
        """Main render loop."""
        self.running = True

        # Initialize terminal
        self._init_terminal()

        # Start keyboard listener thread
        keyboard_thread = threading.Thread(target=self._keyboard_listener, daemon=True)
        keyboard_thread.start()

        try:
            last_frame_time = time.time()
            self.last_resize_check = time.time()

            while self.running:
                current_time = time.time()
                elapsed = current_time - last_frame_time

                # Check for terminal resize periodically
                if current_time - self.last_resize_check >= self.resize_check_interval:
                    self._check_resize()
                    self.last_resize_check = current_time

                # Process updates from background threads
                self._process_update_queue()

                # More frames per second while recording -> smoother waveform
                target_fps = 30 if self.current_status == "recording" else 10
                frame_time = 1.0 / target_fps

                # Render frame if needed and enough time has passed
                if self.needs_render and elapsed >= frame_time:
                    self._render_frame()
                    self.needs_render = False
                    last_frame_time = current_time
                else:
                    # Sleep for remaining frame time (must use dynamic frame_time,
                    # not self.frame_time, or the loop is capped at 10 FPS always).
                    # Cap sleep so quit (q) is processed promptly even at low FPS.
                    sleep_time = min(frame_time - elapsed, 0.05)
                    if sleep_time > 0:
                        time.sleep(sleep_time)

        except KeyboardInterrupt:
            # Ctrl+C: exit the loop immediately; cleanup runs in finally.
            self.running = False
        finally:
            self._cleanup_terminal()

    def exit(self):
        """Stop render loop."""
        self.running = False

    # === Controller Interface Methods (same as Textual app) ===

    def set_status(self, status: str, message: str = ""):
        """Update status (called from controller).

        Args:
            status: New status (idle, recording, processing, complete, error)
            message: Optional status message
        """
        try:
            with open("debug.log", "a") as f:
                f.write(f"set_status queued: {status}, msg: {message[:50]}\n")
        except:
            pass
        self.update_queue.put(('set_status', status, message))

    def update_recording_metrics(self, duration: float, audio_level: float, peak_level: float):
        """Update recording metrics (called every 0.1s).

        Args:
            duration: Recording duration in seconds
            audio_level: Current audio level (0.0 to 1.0)
            peak_level: Peak audio level (0.0 to 1.0)
        """
        self.update_queue.put(('update_metrics', duration, audio_level, peak_level))

    def set_transcription(self, text: str, copied: bool = False, auto_typed: bool = False):
        """Display transcription result.

        Args:
            text: Transcribed text
            copied: Whether text was copied to clipboard
            auto_typed: Whether text was auto-typed
        """
        try:
            with open("debug.log", "a") as f:
                f.write(f"set_transcription called: text_len={len(text)}, copied={copied}, auto_typed={auto_typed}\n")
        except:
            pass
        self.update_queue.put(('set_transcription', text, copied, auto_typed))

    def update_transcription(self, formatted_text: str):
        """Update latest transcription.

        Args:
            formatted_text: Updated formatted text
        """
        self.update_queue.put(('update_transcription', formatted_text))

    def show_error(self, error_message: str):
        """Show error message.

        Args:
            error_message: Error message to display
        """
        self.update_queue.put(('show_error', error_message))

    def call_from_thread(self, method, *args, **kwargs):
        """Thread-safe method calls (replaces Textual's version).

        Args:
            method: Method to call
            *args: Arguments to pass to method
            **kwargs: Keyword arguments to pass to method
        """
        # Simply execute the method - queue handling is done internally
        method(*args, **kwargs)

    # === Internal Methods ===

    def _init_terminal(self):
        """Initialize terminal for rendering."""
        # Switch to alternate screen buffer and hide cursor
        sys.stdout.write("\033[?1049h")  # Alternate screen buffer
        sys.stdout.write("\033[?25l")    # Hide cursor
        # Don't clear screen here; first render will fill entire buffer
        sys.stdout.flush()

        # Log actual terminal and buffer sizes for debugging
        try:
            import shutil
            term_size = shutil.get_terminal_size()
            with open("debug.log", "a") as f:
                f.write(f"\n=== Terminal Init ===\n")
                f.write(f"Detected terminal: {term_size.columns}x{term_size.lines}\n")
                f.write(f"Layout UI size: {self.layout.UI_WIDTH}x{self.layout.UI_HEIGHT}\n")
                f.write(f"Buffer size: {self.buffer.width}x{self.buffer.height}\n")
                f.write(f"History start row: {self.layout.HISTORY_START}, height: {self.layout.HISTORY_HEIGHT}\n")
                f.write(f"History total rows needed: {self.layout.HISTORY_START + self.layout.HISTORY_HEIGHT + 1}\n")
        except Exception as e:
            with open("debug.log", "a") as f:
                f.write(f"Terminal size detect error: {e}\n")

    def _on_ui_key_event(self, event):
        """Handle raw key events for the UI (settings, navigation, quit)."""
        if event.event_type == 'down':
            try:
                key = event.name.lower() if event.name else ''
                if key:
                    self._process_key_in_main_loop(key)
            except Exception as e:
                try:
                    with open("debug.log", "a") as f:
                        f.write(f"Key event processing error: {e}\n")
                except:
                    pass

    def rehook_ui_keys(self):
        """Re-register the UI keyboard hook.

        Required after controller.reconfigure_hotkey() calls keyboard.unhook_all(),
        which would otherwise leave the TUI deaf (no esc/q/navigation).
        """
        if keyboard is None:
            return False
        try:
            keyboard.hook(self._on_ui_key_event)
            try:
                with open("debug.log", "a") as f:
                    f.write("Re-registered keyboard.hook for UI keys\n")
            except:
                pass
            return True
        except Exception as e:
            try:
                with open("debug.log", "a") as f:
                    f.write(f"Failed to re-register UI keys hook: {e}\n")
            except:
                pass
            return False

    def _keyboard_listener(self):
        """Listen for keyboard input using the keyboard library hook."""
        try:
            with open("debug.log", "a") as f:
                f.write("Keyboard listener thread started (using keyboard.hook)\n")

            if keyboard is None:
                with open("debug.log", "a") as f:
                    f.write("Keyboard library not available, UI keyboard disabled\n")
                return

            keyboard.hook(self._on_ui_key_event)
            with open("debug.log", "a") as f:
                f.write("Registered keyboard.hook for UI keys\n")

            # Keep thread alive while running
            while self.running:
                time.sleep(0.1)

            with open("debug.log", "a") as f:
                f.write("Keyboard listener thread exiting (self.running=False)\n")
        except Exception as e:
            with open("debug.log", "a") as f:
                f.write(f"Keyboard listener fatal error: {e}\n")

    def _process_key_in_main_loop(self, key):
        """Route keypress to appropriate handler based on current mode."""
        # Global quit (works in any mode)
        if key == 'q':
            self.exit()
            return

        if not self.settings_mode:
            # Main UI mode
            if key == 'c':
                self.history.clear()
                self.needs_render = True
            elif key == 's':
                # Enter settings mode
                self.settings_mode = True
                self.settings_cursor = 0
                self.settings_editing = False
                self.in_hotkey_capture = False
                self.settings_message = ""
                self.needs_render = True
        else:
            # Settings mode
            if self.in_hotkey_capture:
                self._handle_hotkey_capture_key(key)
            elif self.settings_editing:
                self._handle_settings_edit_key(key)
            else:
                self._handle_settings_navigation_key(key)

    def _handle_settings_navigation_key(self, key):
        """Handle navigation keys in settings mode."""
        if key == 'esc':  # Cancel
            self.settings_mode = False
            self.needs_render = True
        elif key in ('w', 'k'):  # Up
            if self.settings_cursor > 0:
                self.settings_cursor -= 1
            self.needs_render = True
        elif key in ('s', 'j'):  # Down
            if self.settings_cursor < len(self.settings_defs) - 1:
                self.settings_cursor += 1
            self.needs_render = True
        elif key in ('e', 'enter'):  # Edit
            setting = self.settings_defs[self.settings_cursor]
            attr_name = setting[1]
            if attr_name == 'hotkey':
                self.in_hotkey_capture = True
                self.needs_render = True
            else:
                self.settings_editing = True
                self.settings_edit_index = self.settings_cursor
                current_value = getattr(self.controller.config, attr_name)
                self.settings_edit_buffer = str(current_value)
                self.needs_render = True

    def _handle_settings_edit_key(self, key):
        """Handle keypresses when editing a setting value."""
        if key == 'esc':  # Cancel
            self.settings_editing = False
            self.settings_edit_buffer = ""
            self.needs_render = True
        elif key == 'enter':  # Submit
            setting = self.settings_defs[self.settings_edit_index]
            attr_name = setting[1]
            type_ = setting[2]
            raw = self.settings_edit_buffer
            try:
                if type_ == 'int':
                    new_value = int(raw)
                elif type_ == 'float':
                    new_value = float(raw)
                elif type_ == 'bool':
                    lowered = raw.lower()
                    if lowered in ('true', '1', 'yes', 'on'):
                        new_value = True
                    elif lowered in ('false', '0', 'no', 'off'):
                        new_value = False
                    else:
                        raise ValueError
                elif type_ == 'choice':
                    new_value = raw
                else:  # string
                    new_value = raw

                # Update config - special handling for hotkey
                if attr_name == 'hotkey':
                    try:
                        self.controller.reconfigure_hotkey(raw)
                        self.settings_message = f"{setting[0]} saved."
                    except Exception as e:
                        self.settings_message = f"Save error: {e}"
                else:
                    setattr(self.controller.config, attr_name, new_value)
                    try:
                        self.controller.config.save()
                        self.settings_message = f"{setting[0]} saved."
                    except Exception as e:
                        self.settings_message = f"Save error: {e}"
                # Exit editing mode
                self.settings_editing = False
                self.settings_edit_buffer = ""
                self.needs_render = True
            except ValueError:
                self.settings_message = f"Invalid value for {setting[0]}"
                self.needs_render = True
        elif key == 'backspace':  # Backspace
            self.settings_edit_buffer = self.settings_edit_buffer[:-1]
            self.needs_render = True
        else:
            # Printable characters and space
            if key == 'space':
                char = ' '
            elif len(key) == 1 and ord(key) >= 32 and ord(key) <= 126:
                char = key
            else:
                # Ignore other named keys (shift, ctrl, etc.)
                return
            self.settings_edit_buffer += char
            self.needs_render = True

    def _handle_hotkey_capture_key(self, key):
        """Handle keypress during hotkey capture (in settings mode)."""
        if key == 'esc':  # Cancel
            self.in_hotkey_capture = False
            self.settings_message = "Hotkey change canceled"
            self.needs_render = True
            return

        # Determine if this key is a modifier and get its normalized name
        is_modifier = False
        normalized_key = key
        if key in ('ctrl', 'control'):
            is_modifier = True
            normalized_key = 'ctrl'
        elif key in ('alt', 'altgr'):
            is_modifier = True
            normalized_key = 'alt'
        elif key == 'shift':
            is_modifier = True
            normalized_key = 'shift'
        elif key in ('win', 'windows', 'cmd'):
            is_modifier = True
            normalized_key = 'win'

        # Build set of all currently pressed modifiers (normalized)
        pressed_mods = []
        if keyboard.is_pressed('ctrl') or keyboard.is_pressed('control'):
            pressed_mods.append('ctrl')
        if keyboard.is_pressed('alt'):
            pressed_mods.append('alt')
        if keyboard.is_pressed('shift'):
            pressed_mods.append('shift')
        if keyboard.is_pressed('win') or keyboard.is_pressed('windows') or keyboard.is_pressed('cmd'):
            pressed_mods.append('win')

        # If the key itself is a modifier and is in the pressed list, exclude it from the modifiers list
        if is_modifier and normalized_key in pressed_mods:
            pressed_mods.remove(normalized_key)

        # Require at least one other modifier in the combination
        if not pressed_mods:
            return

        # Construct hotkey string: sort modifiers alphabetically for consistency
        modifiers_sorted = sorted(pressed_mods)
        new_hotkey = '+'.join(modifiers_sorted + [normalized_key])

        # Reconfigure hotkey
        self.controller.reconfigure_hotkey(new_hotkey)
        self.in_hotkey_capture = False
        self.settings_message = f"Hotkey set to {new_hotkey}"
        self.needs_render = True

    def _cleanup_terminal(self):
        """Cleanup terminal state."""
        sys.stdout.write("\033[?25h")    # Show cursor
        sys.stdout.write("\033[2J")      # Clear screen
        sys.stdout.write("\033[H")       # Home cursor
        sys.stdout.write("\033[?1049l")  # Switch back to main screen buffer
        sys.stdout.flush()

    def _check_resize(self):
        """Check if terminal was resized and adapt layout."""
        if self.layout.check_and_resize():
            # Terminal size changed - recreate buffer and update components
            self.buffer = ASCIIScreenBuffer(self.layout.UI_WIDTH, self.layout.UI_HEIGHT)

            # Update component sizes
            self.waveform = ASCIIWaveformVisualizer(
                width=self.layout.PANEL_WIDTH - 4,
                attack=0.5,
                release=0.07,
                field_height=self.layout.WAVEFORM_HEIGHT - 2
            )
            self.history.max_visible = self.layout.HISTORY_HEIGHT - 2

            # Mark for render; next frame will overwrite everything
            self.needs_render = True

    def _process_update_queue(self):
        """Process all pending updates from threads."""
        processed = 0
        max_updates_per_frame = 10

        while not self.update_queue.empty() and processed < max_updates_per_frame:
            try:
                msg = self.update_queue.get_nowait()
                self._handle_update(msg)
                processed += 1
            except queue.Empty:
                break

    def _handle_update(self, msg):
        """Handle update message.

        Args:
            msg: Update message tuple
        """
        cmd = msg[0]

        if cmd == 'set_status':
            _, status, message = msg
            self.current_status = status
            self.status_message = message
            # Reset waveform when recording starts
            if status == "recording":
                self.waveform.clear()
            self.needs_render = True

        elif cmd == 'update_metrics':
            _, duration, level, peak = msg

            # Always advance the waveform buffer on every metrics message so the
            # wave keeps scrolling (even during silence/breaks in speech, level
            # naturally falls to 0 and the flat line continues moving).
            self.recording_duration = duration
            self.audio_level = level
            self.peak_level = peak
            self.prev_duration = duration
            self.prev_level = level
            self.prev_peak = peak
            self.waveform.update(level)

            # Mark for render
            self.needs_render = True

        elif cmd == 'set_transcription':
            _, text, copied, auto_typed = msg
            with open("debug.log", "a") as f:
                f.write(f"set_transcription: text len={len(text)}, copied={copied}, auto_typed={auto_typed}\n")
            self.current_status = "complete"
            self.status_message = text[:50] + "..." if len(text) > 50 else text
            self.history.add_entry(datetime.now(), text)
            with open("debug.log", "a") as f:
                f.write(f"History now has {len(self.history.entries)} entries\n")
            self.needs_render = True
            # Auto-transition to idle after 2s
            def transition_to_idle():
                time.sleep(2.0)
                self.set_status("idle")
            threading.Thread(target=transition_to_idle, daemon=True).start()

        elif cmd == 'update_transcription':
            _, formatted_text = msg
            # Update the most recent history entry
            if self.history.entries:
                timestamp, _ = self.history.entries[0]
                self.history.entries[0] = (timestamp, formatted_text)
                self.needs_render = True

        elif cmd == 'show_error':
            _, error_message = msg
            self.current_status = "error"
            self.status_message = error_message
            self.needs_render = True

    def _render_frame(self):
        """Render complete frame to buffer and flush to terminal."""
        self.buffer.clear()
        if self.settings_mode:
            self._render_settings_content()
        else:
            self._render_normal_content()
        self.buffer.render_to_terminal()

    def _render_normal_content(self):
        """Render the main application UI (when not in settings)."""
        # 1. Header
        header_text = f"Voice-to-Text TUI | Status: {self.current_status.title()}"
        self.buffer.center_text(self.layout.HEADER_ROW, header_text)
        self.buffer.write_text(0, self.layout.HEADER_SEPARATOR, '-' * self.layout.UI_WIDTH)

        # 2. Status Panel
        self.buffer.draw_box(
            self.layout.PANEL_MARGIN,
            self.layout.STATUS_PANEL_START,
            self.layout.PANEL_WIDTH,
            self.layout.STATUS_PANEL_HEIGHT,
            title="Status Panel"
        )
        panel_content = self.status_panel.render(
            self.current_status,
            self.recording_duration,
            self.audio_level,
            self.status_message
        )
        for i, line in enumerate(panel_content):
            self.buffer.write_text(
                self.layout.PANEL_MARGIN + 1,
                self.layout.STATUS_PANEL_START + 1 + i,
                line,
                max_width=self.layout.PANEL_WIDTH - 2
            )

        # 3. Waveform (only when recording)
        if self.current_status == "recording":
            self.buffer.draw_box(
                self.layout.PANEL_MARGIN,
                self.layout.WAVEFORM_START,
                self.layout.PANEL_WIDTH,
                self.layout.WAVEFORM_HEIGHT,
                title="Waveform Visualization"
            )
            waveform_lines = self.waveform.render()
            for i, line in enumerate(waveform_lines):
                self.buffer.write_text(
                    self.layout.PANEL_MARGIN + 2,
                    self.layout.WAVEFORM_START + 1 + i,
                    line,
                    max_width=self.layout.PANEL_WIDTH - 4
                )

            # 4. Metrics Row (only when recording)
            metrics_text = self.metrics.render(
                self.recording_duration,
                self.audio_level,
                self.peak_level
            )
            self.buffer.write_text(
                self.layout.PANEL_MARGIN,
                self.layout.METRICS_ROW,
                metrics_text,
                max_width=self.layout.PANEL_WIDTH
            )

        # 5. History Title
        self.buffer.write_text(
            self.layout.PANEL_MARGIN,
            self.layout.HISTORY_TITLE_ROW,
            "Recent Transcriptions:"
        )
        self.buffer.write_text(
            0,
            self.layout.HISTORY_SEPARATOR,
            '-' * self.layout.UI_WIDTH
        )

        # 6. History Box
        self.buffer.draw_box(
            self.layout.PANEL_MARGIN,
            self.layout.HISTORY_START,
            self.layout.PANEL_WIDTH,
            self.layout.HISTORY_HEIGHT
        )

        # Show entry count in history box (subtle)
        entry_count_text = f"({len(self.history.entries)} entries)"
        self.buffer.write_text(
            self.layout.PANEL_MARGIN + self.layout.PANEL_WIDTH - len(entry_count_text) - 2,
            self.layout.HISTORY_START,
            entry_count_text
        )

        history_lines = self.history.render(
            height=self.layout.HISTORY_HEIGHT - 2,
            max_width=self.layout.PANEL_WIDTH - 4
        )
        with open("debug.log", "a") as f:
            f.write(f"_render_frame: rendering {len(history_lines)} history lines\n")
        for i, line in enumerate(history_lines):
            self.buffer.write_text(
                self.layout.PANEL_MARGIN + 2,
                self.layout.HISTORY_START + 1 + i,  # Start at row 1 (after title)
                line,
                max_width=self.layout.PANEL_WIDTH - 4
            )

        # 7. Footer
        self.buffer.write_text(
            0,
            self.layout.FOOTER_SEPARATOR,
            '-' * self.layout.UI_WIDTH
        )
        # Display actual hotkey from config
        hotkey_display = self.config.hotkey.replace('+', '+').title()
        footer_text = f"[{hotkey_display}] Record | [Q] Quit | [S] Settings | [C] Clear"
        self.buffer.center_text(self.layout.FOOTER_ROW, footer_text)

    def _render_settings_content(self):
        """Render the settings screen."""
        # Header
        title = "SETTINGS"
        self.buffer.center_text(0, title)
        self.buffer.write_text(0, 1, '-' * self.layout.UI_WIDTH)

        # Layout parameters
        header_rows = 2
        footer_separator_row = self.layout.FOOTER_SEPARATOR
        footer_row = self.layout.FOOTER_ROW
        start_row = 2  # after header separator
        available = footer_separator_row - start_row
        visible_count = min(len(self.settings_defs), available)

        # Draw each setting
        for i in range(visible_count):
            y = start_row + i
            setting = self.settings_defs[i]
            display_name = setting[0]
            attr_name = setting[1]
            current_value = getattr(self.controller.config, attr_name)
            line = f"  {display_name}: {current_value}"
            if i == self.settings_cursor:
                # Highlight with > prefix
                if len(line) >= 2:
                    line = ">" + line[1:]
                else:
                    line = ">" + line
                self.buffer.write_text(2, y, line, max_width=self.layout.PANEL_WIDTH-4)
            else:
                self.buffer.write_text(2, y, line, max_width=self.layout.PANEL_WIDTH-4)

        # Draw footer separator line
        self.buffer.write_text(0, footer_separator_row, '-' * self.layout.UI_WIDTH)

        # Show temporary message or instructions on footer row
        if self.settings_message:
            self.buffer.write_text(2, footer_row, self.settings_message[:self.layout.UI_WIDTH-4])
        elif self.in_hotkey_capture:
            prompt = "Press new hotkey (modifier+key), Esc to cancel"
            self.buffer.write_text(2, footer_row, prompt[:self.layout.UI_WIDTH-4])
        elif self.settings_editing:
            setting = self.settings_defs[self.settings_edit_index]
            prompt = f"Enter new value for {setting[0]}: {self.settings_edit_buffer}"
            self.buffer.write_text(2, footer_row, prompt[:self.layout.UI_WIDTH-4])
        else:
            instructions = "W/S: Move   E: Edit   Esc: Exit"
            self.buffer.write_text(2, footer_row, instructions[:self.layout.UI_WIDTH-4])
