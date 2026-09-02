"""Audio recording module using sounddevice."""

import numpy as np
import sounddevice as sd
from typing import Optional, Dict, Any


class AudioRecorderError(Exception):
    """Base exception for audio recorder errors."""
    pass


class NoMicrophoneError(AudioRecorderError):
    """Raised when no microphone device is found."""
    pass


class AudioRecorder:
    """Records audio from the default microphone."""

    def __init__(self, sample_rate: int = 16000):
        """Initialize the audio recorder.

        Args:
            sample_rate: Sample rate for recording in Hz (default: 16000).

        Raises:
            NoMicrophoneError: If no input device is found.
        """
        self.sample_rate = sample_rate
        self._recording = False
        self._audio_data = []
        self._current_level = 0.0  # Real-time audio level
        self._peak_level = 0.0  # Peak hold level
        self._smoothed_level = 0.0  # Envelope follower level
        self._last_callback_status = ""
        self._overflow_count = 0

        # Attack/release smoothing (direction A): fast rise with voice,
        # slow gentle settle when you stop or pause.
        self._attack_alpha = 0.50
        self._release_alpha = 0.10

        # Check for microphone availability
        device_info = self.get_default_device()
        if device_info is None:
            raise NoMicrophoneError(
                "No microphone detected. Please connect a microphone and try again."
            )

    def get_default_device(self) -> Optional[Dict[str, Any]]:
        """Get information about the default input device.

        Returns:
            Device info dictionary or None if no device found.
        """
        try:
            device_id = sd.default.device[0]  # Input device
            if device_id is None or device_id < 0:
                return None

            device_info = sd.query_devices(device_id, 'input')
            return device_info
        except (sd.PortAudioError, ValueError):
            return None

    @property
    def is_recording(self) -> bool:
        """Check if currently recording.

        Returns:
            True if recording is in progress, False otherwise.
        """
        return self._recording

    def get_current_level(self) -> float:
        """Get the current audio input level (smoothed).

        Returns:
            Audio level from 0.0 (silence) to 1.0 (loud)
        """
        return self._current_level

    def get_peak_level(self) -> float:
        """Get the peak audio level with decay.

        Returns:
            Peak audio level from 0.0 to 1.0
        """
        return self._peak_level

    def start_recording(self) -> None:
        """Start recording audio from the microphone.

        Raises:
            AudioRecorderError: If already recording.
        """
        if self._recording:
            raise AudioRecorderError("Recording already in progress")

        self._recording = True
        self._audio_data = []

    def _audio_callback(self, indata, frames, time, status):
        """Callback for sounddevice to collect audio data.

        MUST stay fast and I/O-free - this runs on the realtime audio thread.
        No print() (blocking console write corrupts the TUI + causes overflow),
        no disk writes per callback.

        Args:
            indata: Input audio data.
            frames: Number of frames.
            time: Time information.
            status: Status flags (e.g. input overflow).
        """
        # Flag overflow/error without touching the console (the UI surfaces it)
        if status:
            self._last_callback_status = str(status)
            self._overflow_count = getattr(self, "_overflow_count", 0) + 1

        if self._recording:
            self._audio_data.append(indata.copy())

            # Calculate current audio level using logarithmic (dB) scaling
            try:
                rms = np.sqrt(np.mean(indata**2))

                # Convert to dB scale (research report recommendation)
                # Map -50 dB (silence) to 0.0, adjusted for sweet spot at 135-140%
                if rms > 1e-6:  # Avoid log(0)
                    db = 20 * np.log10(rms)
                    # Map dB range: -50 dB = 0%, 0 dB = 100% (tighter range for better sensitivity)
                    normalized_level = (db + 50.0) / 50.0  # -50 to 0 dB -> 0 to 1
                    normalized_level = min(1.0, max(0.0, normalized_level))
                else:
                    normalized_level = 0.0

                # Soft noise floor: taper smoothly toward 0 below threshold
                # instead of hard-snapping to 0 (kills the "pop" on silence).
                if normalized_level < 0.1:
                    normalized_level = normalized_level * (normalized_level / 0.1)

                # Attack/release smoothing (direction A): rise fast with voice,
                # settle slowly when you stop/pause - no abrupt contractions.
                if normalized_level > self._smoothed_level:
                    alpha = self._attack_alpha       # fast attack
                else:
                    alpha = self._release_alpha      # slow release
                self._smoothed_level = (alpha * normalized_level +
                                       (1.0 - alpha) * self._smoothed_level)

                # Peak hold with decay
                if self._smoothed_level > self._peak_level:
                    self._peak_level = self._smoothed_level
                else:
                    self._peak_level *= 0.95  # Decay rate

                # Set current level (no disk I/O here - realtime thread)
                self._current_level = self._smoothed_level
            except Exception as e:
                self._current_level = 0.0

    def get_callback_status(self) -> str:
        """Return the last audio callback status (e.g. input overflow), if any."""
        return getattr(self, "_last_callback_status", "")

    def stop_recording(self) -> np.ndarray:
        """Stop recording and return the recorded audio.

        Returns:
            Numpy array of recorded audio data (float32, mono).

        Raises:
            AudioRecorderError: If not currently recording.
        """
        if not self._recording:
            raise AudioRecorderError("No recording in progress")

        self._recording = False

        if not self._audio_data:
            return np.array([], dtype=np.float32)

        # Concatenate all recorded chunks
        audio = np.concatenate(self._audio_data, axis=0)

        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)

        return audio.flatten().astype(np.float32)

    def record_stream(self):
        """Create a recording stream context manager.

        Usage:
            with recorder.record_stream():
                # Recording happens here
                time.sleep(5)
            audio = recorder.stop_recording()
        """
        return sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=self._audio_callback,
            dtype=np.float32,
            # Larger buffer = fewer overflows on Windows (64ms at 16kHz).
            # Latency is irrelevant for a held-hotkey recorder.
            blocksize=1024
        )

    def record_blocking(self, duration: float) -> np.ndarray:
        """Record audio for a fixed duration (blocking).

        Args:
            duration: Duration to record in seconds.

        Returns:
            Numpy array of recorded audio data.
        """
        recording = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.float32
        )
        sd.wait()  # Wait for recording to complete
        return recording.flatten()
