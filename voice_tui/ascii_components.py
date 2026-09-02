"""ASCII Components - Rendering logic for UI sections."""

import threading
from typing import List, Tuple
from datetime import datetime


def format_time(seconds: float) -> str:
    """Format seconds as MM:SS.ms

    Args:
        seconds: Time in seconds

    Returns:
        Formatted string like "00:03.45"
    """
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:05.2f}"


def create_ascii_bar(level: float, width: int, fill: str = '#', empty: str = '.') -> str:
    """Create ASCII progress bar.

    Args:
        level: Fill level (0.0 to 1.0)
        width: Total width in characters
        fill: Character for filled portion
        empty: Character for empty portion

    Returns:
        Progress bar string like "####....."
    """
    level = max(0.0, min(1.0, level))
    filled = int(level * width)
    return fill * filled + empty * (width - filled)


class ASCIIStatusPanel:
    """Renders status panel content based on application state."""

    def __init__(self, hotkey: str = "Ctrl+Win"):
        """Initialize status panel.

        Args:
            hotkey: Hotkey string to display in instructions.
        """
        self.hotkey = hotkey

    def set_hotkey(self, hotkey: str):
        """Update the displayed hotkey."""
        self.hotkey = hotkey

    def render(self, state: str, duration: float, level: float, message: str) -> List[str]:
        """Returns list of strings for panel interior.

        Args:
            state: Current state (idle, recording, processing, complete, error)
            duration: Recording duration in seconds
            level: Audio level (0.0 to 1.0)
            message: Status message

        Returns:
            List of strings to display inside status panel
        """
        # Format hotkey for display: capitalize parts, show like Ctrl+Shift+Z
        hotkey_display = self.hotkey.replace('+', '+').title()
        if state == "idle":
            return [
                "",
                "  * READY TO RECORD",
                "",
                f"  Hold [{hotkey_display}] to record",
                ""
            ]
        elif state == "recording":
            timer = format_time(duration)
            level_bar = create_ascii_bar(level, width=20)
            percent = int(level * 100)
            return [
                "",
                "  * RECORDING",
                "",
                f"  Recording: {timer}",
                f"  Level: [{level_bar}] {percent}%",
            ]
        elif state == "processing":
            return [
                "",
                "  TRANSCRIBING...",
                "",
                "  Please wait",
                ""
            ]
        elif state == "complete":
            # Truncate message to fit
            display_msg = message[:60] + "..." if len(message) > 60 else message
            return [
                "",
                "  * TRANSCRIPTION COMPLETE",
                "",
                f"  {display_msg}",
                ""
            ]
        elif state == "error":
            display_msg = message[:60] + "..." if len(message) > 60 else message
            return [
                "",
                "  X ERROR",
                "",
                f"  {display_msg}",
                ""
            ]
        else:
            return [
                "",
                f"  Unknown state: {state}",
                "",
                "",
                ""
            ]


class ASCIIWaveformVisualizer:
    """Renders waveform using diagonal Unicode characters for smooth sine-wave visualization."""

    def __init__(self, width: int = 80, smoothing: float = 0.5):
        """Initialize waveform visualizer.

        Args:
            width: Width of waveform in characters
            smoothing: Smoothing factor for EMA (0.0 = no smoothing, 1.0 = fully static)
        """
        self.width = width
        self.buffer = [0.0] * width
        self.smoothing = smoothing  # EMA factor: new_smoothed = smoothing * old + (1-smoothing) * new
        self.smoothed_level = 0.0

    def clear(self):
        """Clear the waveform buffer (reset to all zeros)."""
        self.buffer = [0.0] * self.width
        self.smoothed_level = 0.0

    def update(self, level: float):
        """Add new level value to buffer (smoothed).

        Args:
            level: Audio level (0.0 to 1.0)
        """
        # Apply EMA smoothing to reduce jitter
        self.smoothed_level = self.smoothing * self.smoothed_level + (1.0 - self.smoothing) * level
        # Shift buffer left and add smoothed value
        self.buffer = self.buffer[1:] + [self.smoothed_level]

    def render(self) -> List[str]:
        """Returns 3 rows of smooth sine-wave using Unicode wave characters.

        Creates pattern like: -⎽__⎽-⎻⎺⎺⎻-⎽__⎽-

        Returns:
            List of 3 strings representing the waveform
        """
        lines = ['', '', '']

        for i, level in enumerate(self.buffer):
            # Map level to height (0.0 to 1.0 -> 0 to 8 positions)
            height = int(level * 8)

            # Create smooth sine-wave using wave characters
            if height == 0:  # Lowest
                lines[0] += ' '
                lines[1] += ' '
                lines[2] += '_'
            elif height == 1:  # Very low
                lines[0] += ' '
                lines[1] += ' '
                lines[2] += '⎽'
            elif height == 2:  # Low
                lines[0] += ' '
                lines[1] += ' '
                lines[2] += '-'
            elif height == 3:  # Below middle
                lines[0] += ' '
                lines[1] += '⎽'
                lines[2] += ' '
            elif height == 4:  # Middle
                lines[0] += ' '
                lines[1] += '-'
                lines[2] += ' '
            elif height == 5:  # Above middle
                lines[0] += ' '
                lines[1] += '⎺'
                lines[2] += ' '
            elif height == 6:  # High
                lines[0] += '⎻'
                lines[1] += ' '
                lines[2] += ' '
            elif height == 7:  # Very high
                lines[0] += '⎺'
                lines[1] += ' '
                lines[2] += ' '
            else:  # Peak
                lines[0] += '-'
                lines[1] += ' '
                lines[2] += ' '

        return lines


class ASCIIMetricsRow:
    """Renders single metrics row showing recording stats."""

    def render(self, duration: float, level: float, peak: float) -> str:
        """Returns formatted metrics string.

        Args:
            duration: Recording duration in seconds
            level: Current audio level (0.0 to 1.0)
            peak: Peak audio level (0.0 to 1.0)

        Returns:
            Formatted string like "Recording: 00:03.45 | Level: [####.....] 45% | Peak: 87%"
        """
        timer = format_time(duration)
        bar = create_ascii_bar(level, width=15)
        percent = int(level * 100)
        peak_percent = int(peak * 100)

        return f"  Recording: {timer} | Level: [{bar}] {percent}% | Peak: {peak_percent}%"


class ASCIIHistoryLog:
    """Renders history entries with timestamps."""

    def __init__(self, max_visible: int = 10, max_entries: int = 100):
        """Initialize history log.

        Args:
            max_visible: Maximum visible entries
            max_entries: Maximum total entries to retain
        """
        self.entries: List[Tuple[datetime, str]] = []
        self.max_visible = max_visible
        self.max_entries = max_entries
        self.scroll_offset = 0
        self.lock = threading.Lock()

    def add_entry(self, timestamp: datetime, text: str):
        """Add new entry (newest first).

        Args:
            timestamp: Entry timestamp
            text: Transcription text
        """
        with self.lock:
            # Insert at beginning (newest first)
            self.entries.insert(0, (timestamp, text))

            # Limit total entries
            if len(self.entries) > self.max_entries:
                self.entries = self.entries[:self.max_entries]

    def clear(self):
        """Clear all history entries (thread-safe)."""
        with self.lock:
            self.entries.clear()

    def render(self, height: int, max_width: int = 82) -> List[str]:
        """Returns list of formatted entry strings.

        Args:
            height: Number of lines available
            max_width: Maximum width for each entry

        Returns:
            List of formatted entry strings
        """
        lines = []

        with self.lock:
            # Calculate visible range (make a copy of the slice to avoid holding lock during formatting)
            visible_entries = list(self.entries[self.scroll_offset:self.scroll_offset + height])

        for timestamp, text in visible_entries:
            # Format: "14:32:15 "This is the transcription...""
            time_str = timestamp.strftime("%H:%M:%S")

            # Calculate available width for text (minus timestamp and quotes)
            text_width = max_width - len(time_str) - 4  # 4 for ' ""' and space

            # Truncate text if needed
            if len(text) > text_width:
                display_text = text[:text_width - 3] + "..."
            else:
                display_text = text

            line = f'{time_str} "{display_text}"'
            lines.append(line)

        # Fill remaining height with empty lines
        while len(lines) < height:
            lines.append("")

        return lines
