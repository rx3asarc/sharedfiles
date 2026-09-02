"""ASCII Components - Rendering logic for UI sections."""

import math
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


def _wrap_text(text: str, width: int) -> List[str]:
    """Wrap text to fit a width, splitting on spaces (word wrap).

    Args:
        text: Text to wrap
        width: Maximum line width

    Returns:
        List of wrapped lines
    """
    if width < 1:
        return []
    words = text.split(' ')
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else current + ' ' + word
        if len(candidate) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            # Long unbreakable word: hard-slice it
            if len(word) > width:
                while len(word) > width:
                    lines.append(word[:width])
                    word = word[width:]
                current = word
            else:
                current = word
    if current:
        lines.append(current)
    return lines


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
    """Renders an organic, ChatGPT/Gemini-style waveform that swells with voice.

    The wave does NOT scroll horizontally (that looked fast and low-res).
    Instead it draws a dense, symmetric, filled waveform that breathes in
    place: your voice envelope modulates the height of several smooth humps,
    and a slow phase drift keeps the shape gently travelling so it always
    feels alive - even during silences.
    """

    def __init__(self, width: int = 80, attack: float = 0.5, release: float = 0.07, field_height: int = 5):
        """Initialize waveform visualizer.

        Args:
            width: Width of waveform in characters
            attack: How fast the hump grows with voice (0..1 per frame)
            release: How slowly it settles when you stop (0..1 per frame)
            field_height: Total interior rows (symmetric around center)
        """
        self.width = max(width, 8)
        self.attack = max(0.02, min(1.0, attack))
        self.release = max(0.005, min(1.0, release))
        self.field_height = max(3, field_height)
        self.center = (self.field_height - 1) // 2  # symmetric axis row
        self.smoothed_level = 0.0
        self.phase = 0.0
        # Single central hump; phase drift keeps it gently alive in silence
        self.phase_step = (2 * math.pi) / 120.0

    def clear(self):
        """Reset waveform state."""
        self.smoothed_level = 0.0
        self.phase = 0.0

    def update(self, level: float):
        """Feed a new audio level (0.0 to 1.0) with attack/release smoothing.

        Direction A: the hump rises fast with your voice (attack) but settles
        slowly when you stop/pause (release), so it never snaps shut.
        """
        level = max(0.0, min(1.0, level))
        if level > self.smoothed_level:
            # Attack: move most of the way to the new level quickly
            self.smoothed_level += self.attack * (level - self.smoothed_level)
        else:
            # Release: creep gently down (a few % per frame)
            self.smoothed_level += self.release * (level - self.smoothed_level)
        # Slow phase drift keeps the shape gently moving during silence
        self.phase = (self.phase + self.phase_step) % (2 * math.pi)

    def _height_at(self, x: int) -> float:
        """Normalized height for one column (0.0 to 1.0).

        ONE centered hump (gaussian) that grows outward from the middle as
        the voice envelope rises - wider AND taller - but keeps visible
        edges (never fills the whole box). A faint ripple keeps it organic.
        """
        env = self.smoothed_level ** 0.6  # root-compress: quiet speech still shows
        cx = (self.width - 1) / 2.0
        # Sigma grows with voice: narrower at silence, wider when loud,
        # so the hump visibly adapts to voice strength.
        sigma = self.width * (0.10 + 0.16 * env)
        if sigma < 2.0:
            sigma = 2.0
        d = (x - cx) / sigma
        gauss = math.exp(-0.5 * d * d)
        # Faint travelling ripple - a hint of life, not separate humps
        ripple = 1.0 + 0.05 * math.sin(2 * math.pi * d * 2.0 + self.phase)
        # Baseline 0.22 keeps a small breathing bump visible in silence
        h = (0.22 + 0.78 * env) * gauss * ripple
        return min(1.0, max(0.0, h))

    def render(self) -> List[str]:
        """Render the waveform as a dense, symmetric hump using half-blocks.

        Each character cell is two visual levels (top half + bottom half via
        the Unicode half-block characters), so a 5-row wave shows ~11 levels
        and a 7-row wave ~15 levels - far more nuance than the old 3-5 chunky
        levels, while using the same terminal rows.

        Returns:
            List of field_height strings, each width chars long.
        """
        F = self.field_height
        c = self.center
        half_side = F  # half-strips per side (e.g. 5 for a 5-row field)
        # half-fill per column: top_fill[row] and bottom_fill[row] booleans
        top = [False] * F
        bottom = [False] * F
        rows = [[' ' for _ in range(self.width)] for _ in range(F)]

        for x in range(self.width):
            h = self._height_at(x)
            n = int(round(h * half_side))  # half-levels above/below midline

            if n <= 0:
                # soft flat baseline at the midline
                rows[c][x] = '─'
                continue

            # Fill n half-strips above the midline, n below (symmetric)
            for k in range(1, n + 1):
                # above: k=1 -> row c top, k=2 -> row c-1 bottom, ...
                if k % 2 == 1:
                    r = c - (k - 1) // 2
                    if r >= 0:
                        top[r] = True
                else:
                    r = c - k // 2
                    if r >= 0:
                        bottom[r] = True
                # below: k=1 -> row c bottom, k=2 -> row c+1 top, ...
                if k % 2 == 1:
                    r = c + (k - 1) // 2
                    if r < F:
                        bottom[r] = True
                else:
                    r = c + k // 2
                    if r < F:
                        top[r] = True

            # Render the column from the half-fill flags
            for r in range(F):
                t, b = top[r], bottom[r]
                if t and b:
                    rows[r][x] = '█'
                elif t:
                    rows[r][x] = '▀'
                elif b:
                    rows[r][x] = '▄'
                # reset flags for next column
                top[r] = False
                bottom[r] = False

        return [''.join(row) for row in rows]


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
        """Returns list of formatted entry strings, wrapping long entries.

        Entries wrap across multiple lines (instead of truncating with ...),
        so multi-sentence transcriptions display fully and read naturally.

        Args:
            height: Number of lines available
            max_width: Maximum width for each entry

        Returns:
            List of formatted entry strings
        """
        lines = []

        with self.lock:
            # Make a copy of the visible slice (avoid holding lock during formatting)
            visible_entries = list(self.entries[self.scroll_offset:self.scroll_offset + height])

        for timestamp, text in visible_entries:
            time_str = timestamp.strftime("%H:%M:%S")
            # Available width for text (minus timestamp + quote/space characters)
            text_width = max_width - len(time_str) - 4  # 4 for ' ""' and space

            first = True
            for chunk in _wrap_text(text, text_width):
                if first:
                    lines.append(f'{time_str} "{chunk}"')
                    first = False
                else:
                    # Continuation line: timestamp area padded, quote continues
                    lines.append(f'{" " * (len(time_str) + 1)}"{chunk}')
                if len(lines) >= height:
                    break
            if len(lines) >= height:
                break

        # Fill remaining height with empty lines
        while len(lines) < height:
            lines.append("")

        return lines
