"""Main application entry point and orchestration."""

import argparse
import sys
import time
import threading
from pathlib import Path

try:
    import keyboard
except ImportError:
    keyboard = None

try:
    import pyperclip
except ImportError:
    pyperclip = None

from .config import Config
from .recorder import AudioRecorder, NoMicrophoneError, AudioRecorderError
from .transcriber import WhisperTranscriber, ModelLoadError, TranscriberError
from .auto_type import AutoTyper
from .ascii_app import VoiceToTextASCIIApp as VoiceToTextApp
from .fast_clipboard import copy_to_clipboard


class VoiceToTextController:
    """Controller that coordinates recording, transcription, and UI."""

    def __init__(self, config: Config):
        """Initialize the controller.

        Args:
            config: Application configuration.
        """
        self.config = config
        self.app: VoiceToTextApp = None
        self.recorder: AudioRecorder = None
        self.transcriber: WhisperTranscriber = None
        self.auto_typer: AutoTyper = None
        self.recording_stream = None
        self.recording_start_time = 0
        self.duration_timer = None
        self.is_shutting_down = False
        self._hotkey_active = False  # Guard against key repeat

    def initialize(self) -> bool:
        """Initialize all components.

        Returns:
            True if initialization successful, False otherwise.
        """
        try:
            # Initialize recorder
            with open("debug.log", "a") as f:
                f.write("Initializing microphone...\n")
            self.recorder = AudioRecorder(sample_rate=self.config.sample_rate)
            device_info = self.recorder.get_default_device()
            with open("debug.log", "a") as f:
                f.write(f"Microphone: {device_info['name']}\n")

            # Initialize transcriber
            print(f"Loading Whisper model '{self.config.model_name}'...")
            print("This may take a moment on first run (downloading model)...")
            self.transcriber = WhisperTranscriber(
                model_name=self.config.model_name,
                language=self.config.language,
                device=self.config.device_type,
                compute_type=self.config.compute_type,
                use_smart_formatting=self.config.use_smart_formatting,
                openrouter_api_key=self.config.openrouter_api_key,
                openrouter_model=self.config.openrouter_model
            )
            model_info = self.transcriber.get_model_info()
            print(f"Model loaded: {model_info['model_name']} "
                  f"(device: {model_info['device']}, "
                  f"compute: {model_info['compute_type']})")

            # Initialize auto-typer
            if self.config.auto_type:
                self.auto_typer = AutoTyper(type_interval=self.config.type_interval)
                if self.auto_typer.is_available:
                    print("Auto-type: enabled")
                else:
                    print("Auto-type: disabled (PyAutoGUI not available)")
            else:
                print("Auto-type: disabled")

            return True

        except NoMicrophoneError as e:
            print(f"\nError: {e}")
            print("\nTroubleshooting:")
            print("1. Check that a microphone is connected")
            print("2. Check microphone permissions in system settings")
            print("3. Try selecting a different microphone")
            return False

        except ModelLoadError as e:
            print(f"\nError loading model: {e}")
            print("\nTroubleshooting:")
            print("1. Check your internet connection (for first-time model download)")
            print("2. Try a different model with --model flag")
            print("3. Ensure you have enough disk space")
            return False

        except Exception as e:
            print(f"\nUnexpected error during initialization: {e}")
            return False

    def start_recording(self):
        """Start audio recording."""
        try:
            with open("debug.log", "a") as f:
                f.write(f"start_recording() called, is_shutting_down={self.is_shutting_down}, is_recording={self.recorder.is_recording if self.recorder else 'no recorder'}\n")
        except:
            pass

        if self.is_shutting_down:
            try:
                with open("debug.log", "a") as f:
                    f.write("Shutting down, aborting start_recording\n")
            except:
                pass
            return

        if self.recorder.is_recording:
            try:
                with open("debug.log", "a") as f:
                    f.write("Already recording, ignoring start\n")
            except:
                pass
            return

        try:
            # Start recorder
            self.recorder.start_recording()
            with open("debug.log", "a") as f:
                f.write("Recorder.start_recording() succeeded\n")

            # Start audio stream
            self.recording_stream = self.recorder.record_stream()
            self.recording_stream.start()
            self.recording_start_time = time.time()
            with open("debug.log", "a") as f:
                f.write(f"Recording stream started at {self.recording_start_time}\n")

            # Update UI
            if self.app:
                self.app.call_from_thread(self.app.set_status, "recording")
                self.app.call_from_thread(self.app.update_recording_metrics, 0.0, 0.0, 0.0)
                with open("debug.log", "a") as f:
                    f.write("UI updated to recording state\n")

            # Start duration timer
            self._start_duration_timer()
            with open("debug.log", "a") as f:
                f.write("start_recording completed\n")

        except Exception as e:
            with open("debug.log", "a") as f:
                f.write(f"start_recording exception: {e}\n")
                import traceback
                traceback.print_exc(file=f)
            if self.app:
                self.app.show_error(f"Recording error: {e}")

    def stop_recording(self):
        """Stop audio recording and process transcription."""
        try:
            with open("debug.log", "a") as f:
                f.write(f"stop_recording() ENTRY, is_shutting_down={self.is_shutting_down}, is_recording={self.recorder.is_recording if self.recorder else 'no recorder'}\n")
        except:
            pass
        if self.is_shutting_down:
            return

        try:
            if not self.recorder.is_recording:
                with open("debug.log", "a") as f:
                    f.write("stop_recording but recorder not recording - ignoring\n")
                return

            # Stop duration timer
            self._stop_duration_timer()
            with open("debug.log", "a") as f:
                f.write("Duration timer stopped\n")

            # Stop recording stream
            if self.recording_stream:
                try:
                    self.recording_stream.stop()
                    self.recording_stream.close()
                    with open("debug.log", "a") as f:
                        f.write("Recording stream stopped and closed\n")
                except Exception as e:
                    with open("debug.log", "a") as f:
                        f.write(f"Error stopping recording stream: {e}\n")
                finally:
                    self.recording_stream = None

            # Get recorded audio
            try:
                audio_data = self.recorder.stop_recording()
                duration = time.time() - self.recording_start_time
                with open("debug.log", "a") as f:
                    f.write(f"Recording stopped: duration={duration:.3f}s, audio shape={audio_data.shape if audio_data is not None else 'None'}\n")
            except Exception as e:
                with open("debug.log", "a") as f:
                    f.write(f"Error in recorder.stop_recording: {e}\n")
                audio_data = None
                duration = 0.0

            # Check minimum duration
            if duration < self.config.min_recording_duration:
                with open("debug.log", "a") as f:
                    f.write(f"Recording too short ({duration:.3f}s < {self.config.min_recording_duration}s), discarding\n")
                if self.app:
                    self.app.call_from_thread(self.app.show_error, "Recording too short")
                    threading.Timer(2.0, lambda: self.app and self.app.call_from_thread(self.app.set_status, "idle")).start()
                return

            # Update UI to processing
            if self.app:
                self.app.call_from_thread(self.app.set_status, "processing", "Transcribing...")
                with open("debug.log", "a") as f:
                    f.write("UI set to processing\n")

            # Transcribe in background thread
            t = threading.Thread(target=self._transcribe_audio, args=(audio_data,), daemon=True)
            t.start()
            with open("debug.log", "a") as f:
                f.write(f"Transcription thread started: {t.ident}\n")

        except Exception as e:
            with open("debug.log", "a") as f:
                f.write(f"Stop recording exception: {e}\n")
                import traceback
                traceback.print_exc(file=f)
            if self.app:
                self.app.show_error(f"Stop recording error: {e}")

    def _transcribe_audio(self, audio_data):
        """Transcribe audio data with fast local formatting.

        Args:
            audio_data: Numpy array of audio data.
        """
        try:
            with open("debug.log", "a") as f:
                f.write("_transcribe_audio: starting transcription\n")
            # Transcribe with local formatting (sub-millisecond, no LLM)
            # skip_formatting=False applies local formatter; LLM formatter disabled in config
            text = self.transcriber.transcribe(audio_data, self.config.sample_rate, skip_formatting=False)
            with open("debug.log", "a") as f:
                f.write(f"_transcribe_audio: got text (len={len(text) if text else 0})\n")

            if not text:
                with open("debug.log", "a") as f:
                    f.write("_transcribe_audio: no text detected\n")
                if self.app:
                    self.app.call_from_thread(self.app.show_error, "No speech detected")
                    threading.Timer(2.0, lambda: self.app and self.app.call_from_thread(self.app.set_status, "idle")).start()
                return

            # Copy to clipboard (use optimized method)
            copied = False
            try:
                with open("debug.log", "a") as f:
                    f.write("_transcribe_audio: copying to clipboard\n")
                copied = copy_to_clipboard(text)
                with open("debug.log", "a") as f:
                    f.write(f"_transcribe_audio: clipboard copy {'succeeded' if copied else 'failed'}\n")
            except Exception as e:
                with open("debug.log", "a") as f:
                    f.write(f"_transcribe_audio: clipboard exception: {e}\n")

            # Auto-paste if enabled and clipboard copy succeeded (send Ctrl+V / Cmd+V)
            if self.config.auto_paste and copied:
                try:
                    if sys.platform == "darwin":
                        keyboard.send('command+v')
                    else:
                        keyboard.send('ctrl+v')
                    with open("debug.log", "a") as f:
                        f.write("_transcribe_audio: sent paste keystroke\n")
                except Exception as e:
                    with open("debug.log", "a") as f:
                        f.write(f"_transcribe_audio: paste failed: {e}\n")

            # Update UI immediately
            if self.app:
                with open("debug.log", "a") as f:
                    f.write("_transcribe_audio: updating UI with set_transcription\n")
                self.app.call_from_thread(self.app.set_transcription, text, copied=copied, auto_typed=False)

            # Auto-type text if enabled (legacy, not recommended)
            if self.config.auto_type and self.auto_typer and self.auto_typer.is_available:
                with open("debug.log", "a") as f:
                    f.write("_transcribe_audio: auto-type enabled (legacy), starting async type\n")
                self.auto_typer.type_text_async(text, lambda success: None)

        except TranscriberError as e:
            with open("debug.log", "a") as f:
                f.write(f"_transcribe_audio: TranscriberError: {e}\n")
            if self.app:
                self.app.call_from_thread(self.app.show_error, f"Transcription failed: {e}")
        except Exception as e:
            with open("debug.log", "a") as f:
                f.write(f"_transcribe_audio: Unexpected error: {e}\n")
            if self.app:
                self.app.call_from_thread(self.app.show_error, f"Unexpected error: {e}")

    def _format_and_update(self, raw_text: str):
        """Background thread to format and update display.

        Args:
            raw_text: Raw transcription text to format.
        """
        try:
            formatted = self.transcriber._format_transcription(raw_text)
            if formatted and formatted != raw_text:
                # Update display with formatted version
                if self.app:
                    self.app.call_from_thread(self.app.update_transcription, formatted)
        except Exception as e:
            # Fail silently, raw text already shown
            print(f"Background formatting failed: {e}")

    def _update_duration(self):
        """Update recording duration, audio level, and peak level in UI."""
        try:
            if self.recorder.is_recording and self.app:
                duration = time.time() - self.recording_start_time
                # Get real-time audio level and peak from microphone
                audio_level = self.recorder.get_current_level()
                peak_level = self.recorder.get_peak_level()
                try:
                    with open("debug.log", "a") as f:
                        f.write(f"_update_duration: dur={duration:.2f}, level={audio_level:.2f}, peak={peak_level:.2f}\n")
                except:
                    pass
                self.app.call_from_thread(self.app.update_recording_metrics, duration, audio_level, peak_level)
        except Exception as e:
            with open("debug.log", "a") as f:
                f.write(f"_update_duration exception: {e}\n")

    def _start_duration_timer(self):
        """Start timer to update recording duration."""
        def timer_loop():
            while self.recorder and self.recorder.is_recording and not self.is_shutting_down:
                self._update_duration()
                time.sleep(0.1)

        self.duration_timer = threading.Thread(target=timer_loop, daemon=True)
        self.duration_timer.start()

    def _stop_duration_timer(self):
        """Stop the duration timer."""
        self.duration_timer = None

    def setup_hotkey(self):
        """Set up global hotkey listener using keyboard.hook for full control."""
        try:
            with open("debug.log", "a") as f:
                f.write(f"Setting up hotkey: {self.config.hotkey}\n")
        except:
            pass
        if keyboard is None:
            print("\nWarning: 'keyboard' library not available.")
            print("Hotkey functionality will not work.")
            return False

        try:
            # Parse hotkey into parts
            hotkey = self.config.hotkey.lower()
            parts = hotkey.split('+')
            if len(parts) < 2:
                with open("debug.log", "a") as f:
                    f.write("Hotkey must include at least one modifier (e.g., ctrl+space)\n")
                return False
            self._hotkey_key = parts[-1]
            self._hotkey_modifiers = set(parts[:-1])
            with open("debug.log", "a") as f:
                f.write(f"Parsed hotkey: key={self._hotkey_key}, modifiers={self._hotkey_modifiers}\n")

            # First try: global hook (most reliable)
            try:
                self._hotkey_hook = keyboard.hook(self._hotkey_event_handler)
                with open("debug.log", "a") as f:
                    f.write("Registered global keyboard hook for hotkey handling\n")
                return True
            except Exception as hook_err:
                with open("debug.log", "a") as f:
                    f.write(f"keyboard.hook failed: {hook_err}\n")
                # Fallback: use add_hotkey
                try:
                    keyboard.add_hotkey(hotkey, self._on_hotkey_press, suppress=False, trigger_on_release=False)
                    keyboard.add_hotkey(hotkey, self._on_hotkey_release, suppress=False, trigger_on_release=True)
                    self._hotkey_hook = None
                    with open("debug.log", "a") as f:
                        f.write("Registered hotkey via add_hotkey (fallback)\n")
                    return True
                except Exception as e2:
                    with open("debug.log", "a") as f:
                        f.write(f"add_hotkey fallback also failed: {e2}\n")
                    return False
        except Exception as e:
            with open("debug.log", "a") as f:
                f.write(f"Failed to setup hotkey: {e}\n")
            print(f"\nWarning: Failed to register hotkey '{self.config.hotkey}': {e}")
            print("You may need to run with administrator/root privileges.")
            return False

    def _hotkey_event_handler(self, event):
        """Handle all keyboard events and filter for hotkey press/release."""
        if keyboard is None:
            return
        try:
            # We only care about key events (not text)
            if event.event_type not in ('down', 'up'):
                return

            key_name = event.name.lower() if event.name else ''

            # Only log raw event for our key to avoid spam
            if key_name == self._hotkey_key:
                with open("debug.log", "a") as f:
                    f.write(f"Hotkey event: {event.event_type}, key={key_name}\n")

            # Check if this event matches our hotkey key
            if key_name != self._hotkey_key:
                return

            # For 'down' events, check if all modifiers are pressed
            if event.event_type == 'down':
                # Check modifiers
                modifiers_ok = True
                mod_checks = []
                if 'ctrl' in self._hotkey_modifiers:
                    pressed = keyboard.is_pressed('ctrl') or keyboard.is_pressed('control')
                    mod_checks.append(f"ctrl={pressed}")
                    if not pressed:
                        modifiers_ok = False
                if 'alt' in self._hotkey_modifiers:
                    pressed = keyboard.is_pressed('alt')
                    mod_checks.append(f"alt={pressed}")
                    if not pressed:
                        modifiers_ok = False
                if 'shift' in self._hotkey_modifiers:
                    pressed = keyboard.is_pressed('shift')
                    mod_checks.append(f"shift={pressed}")
                    if not pressed:
                        modifiers_ok = False
                if 'win' in self._hotkey_modifiers:
                    pressed = keyboard.is_pressed('win') or keyboard.is_pressed('windows') or keyboard.is_pressed('cmd')
                    mod_checks.append(f"win={pressed}")
                    if not pressed:
                        modifiers_ok = False
                with open("debug.log", "a") as f:
                    f.write(f"Modifier check: {', '.join(mod_checks)} => {modifiers_ok}\n")
                if modifiers_ok:
                    self._on_hotkey_press()
                else:
                    # Too noisy; could comment out
                    pass
            else:  # 'up'
                with open("debug.log", "a") as f:
                    f.write("Hotkey up event received\n")
                self._on_hotkey_release()
        except Exception as e:
            with open("debug.log", "a") as f:
                f.write(f"Hotkey handler error: {e}\n")

    def _on_hotkey_press(self):
        """Handle hotkey press event (triggered by add_hotkey or hook)."""
        import sys
        sys.stderr.write("[PRESS] Hotkey press event\n")
        sys.stderr.flush()
        try:
            with open("debug.log", "a") as f:
                f.write("Hotkey press event (handler entry)\n")
        except:
            pass
        # Guard against multiple presses
        if self._hotkey_active:
            try:
                with open("debug.log", "a") as f:
                    f.write("Already recording, ignoring extra press\n")
            except:
                pass
            return
        self._hotkey_active = True
        try:
            self.start_recording()
        except Exception as e:
            with open("debug.log", "a") as f:
                f.write(f"start_recording exception in press handler: {e}\n")
            self._hotkey_active = False  # reset on error

    def _on_hotkey_release(self):
        """Handle hotkey release event (triggered by add_hotkey or hook)."""
        import sys
        sys.stderr.write("[RELEASE] Hotkey release event\n")
        sys.stderr.flush()
        try:
            with open("debug.log", "a") as f:
                f.write("Hotkey release event (handler entry)\n")
        except:
            pass
        # Reset flag regardless
        was_active = self._hotkey_active
        self._hotkey_active = False
        if was_active and self.recorder and self.recorder.is_recording:
            try:
                with open("debug.log", "a") as f:
                    f.write("Stopping recording on release - calling stop_recording()\n")
                self.stop_recording()
            except Exception as e:
                with open("debug.log", "a") as f:
                    f.write(f"Exception during stop_recording: {e}\n")
                    import traceback
                    traceback.print_exc(file=open("debug.log", "a"))
        else:
            try:
                with open("debug.log", "a") as f:
                    f.write("Release ignored (was_active=%s, recorder=%s, is_recording=%s)\n" % (was_active, self.recorder is not None, self.recorder.is_recording if self.recorder else 'n/a'))
            except:
                pass

    def run(self):
        """Run the application."""
        # Create and run TUI app
        self.app = VoiceToTextApp(
            config=self.config,
            controller=self
        )

        # Setup hotkey in background
        hotkey_ready = self.setup_hotkey()

        if not hotkey_ready:
            print("Continuing without hotkey support...")

        # Run the app
        try:
            self.app.run()
        finally:
            self.shutdown()

    def shutdown(self):
        """Clean up resources."""
        self.is_shutting_down = True

        # Stop recording if active
        if self.recorder and self.recorder.is_recording:
            try:
                if self.recording_stream:
                    self.recording_stream.stop()
                    self.recording_stream.close()
                self.recorder.stop_recording()
            except:
                pass

        # Unhook keyboard
        if keyboard:
            try:
                keyboard.unhook_all()
            except:
                pass

    def reconfigure_hotkey(self, new_hotkey: str):
        """Reconfigure the hotkey at runtime and save to config."""
        self.config.hotkey = new_hotkey
        if self.app:
            self.app.config.hotkey = new_hotkey
            self.app.status_panel.set_hotkey(new_hotkey)
            self.app.needs_render = True
        try:
            self.config.save()
            with open("debug.log", "a") as f:
                f.write(f"reconfigure_hotkey: saved new hotkey {new_hotkey}\n")
        except Exception as e:
            with open("debug.log", "a") as f:
                f.write(f"reconfigure_hotkey: save error: {e}\n")
        # Update parsed hotkey for hook handler
        try:
            hotkey = new_hotkey.lower()
            parts = hotkey.split('+')
            if len(parts) >= 2:
                self._hotkey_key = parts[-1]
                self._hotkey_modifiers = set(parts[:-1])
                with open("debug.log", "a") as f:
                    f.write(f"reconfigure_hotkey: parsed key={self._hotkey_key}, modifiers={self._hotkey_modifiers}\n")
        except Exception as e:
            with open("debug.log", "a") as f:
                f.write(f"reconfigure_hotkey: parse error: {e}\n")
        # Attempt to re-register the hotkey immediately (hot-reload)
        try:
            if keyboard:
                keyboard.unhook_all()
                with open("debug.log", "a") as f:
                    f.write("reconfigure_hotkey: unhooked all hooks\n")
                if self.setup_hotkey():
                    with open("debug.log", "a") as f:
                        f.write("reconfigure_hotkey: new hotkey registered successfully\n")
                else:
                    with open("debug.log", "a") as f:
                        f.write("reconfigure_hotkey: failed to register new hotkey\n")
        except Exception as e:
            with open("debug.log", "a") as f:
                f.write(f"reconfigure_hotkey: hot-reload error: {e}\n")


def parse_arguments():
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Voice-to-Text TUI with hotkey recording and local Whisper transcription."
    )

    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Whisper model to use (tiny, base, small, medium, large-v2, large-v3). Default: base"
    )

    parser.add_argument(
        "--language",
        type=str,
        default=None,
        help="Language code for transcription (e.g., 'en', 'es') or 'auto'. Default: en"
    )

    parser.add_argument(
        "--hotkey",
        type=str,
        default=None,
        help="Hotkey combination for recording (e.g., 'ctrl+win'). Default: ctrl+win"
    )

    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to config.yaml file. Default: ./config.yaml"
    )

    return parser.parse_args()


def main():
    """Main entry point for the application."""
    print("Voice-to-Text TUI Application")
    print("=" * 50)

    # Parse arguments
    args = parse_arguments()

    # Load configuration
    config = Config.load(args.config)
    config.update_from_args(args)

    print(f"\nConfiguration:")
    print(f"  Model: {config.model_name}")
    print(f"  Language: {config.language}")
    print(f"  Hotkey: {config.hotkey}")
    print(f"  Sample Rate: {config.sample_rate}Hz")
    print()

    # Create controller
    controller = VoiceToTextController(config)

    # Initialize components
    if not controller.initialize():
        print("\nInitialization failed. Exiting.")
        sys.exit(1)

    print("\nStarting TUI application...")
    print("=" * 50)
    print()

    # Run the application
    try:
        controller.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)

    print("Goodbye!")


if __name__ == "__main__":
    main()
