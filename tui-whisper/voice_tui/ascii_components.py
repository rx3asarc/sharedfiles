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
        self.center = (self.field_height * 4) // 2  # symmetric axis in sub-pixels
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
        # Moderate sigma: not too spread out, grows a bit with voice
        sigma = self.width * (0.05 + 0.07 * env)
        if sigma < 1.5:
            sigma = 1.5
        d = (x - cx) / sigma
        gauss = math.exp(-0.5 * d * d)
        # Ripple - a travelling shimmer; strong enough to be visible even at
        # silence so the small bump keeps breathing (must cross quantization).
        ripple = 1.0 + 0.15 * math.sin(2 * math.pi * d * 2.0 + self.phase)
        # Baseline 0.26 keeps a small breathing bump visible in silence
        h = (0.26 + 0.74 * env) * gauss * ripple
        return min(1.0, max(0.0, h))

    @staticmethod
    def _braille_bit(v: int, col: int) -> int:
        """Braille dot bit for sub-row v (0-3) and sub-col col (0-1)."""
        LEFT = (0x01, 0x02, 0x04, 0x40)   # dots 1,2,3,7
        RIGHT = (0x08, 0x10, 0x20, 0x80)  # dots 4,5,6,8
        return LEFT[v] if col == 0 else RIGHT[v]

    def render(self) -> List[str]:
        """Render the waveform as a smooth, solid hump at braille resolution.

        Uses FULL braille sub-pixels (4 levels per character row, 2 per
        column) so a wave with F interior rows has F*4 vertical levels
        (7 rows = 28 levels - 8-10x the original chunky blocks). The body is
        solid (like the earlier half-block look you liked) but the contour is
        smooth, and a single-dot thin baseline appears only near the hump.

        Returns:
            List of field_height strings, each width chars long.
        """
        F = self.field_height
        V = F * 4                     # vertical sub-pixels
        center = V // 2               # axis between sub-rows center-1/center
        mid_sub = center - 1          # exact middle sub-row (baseline)
        half = V // 2                 # max half-fill per side
        W = self.width

        mask = [[0] * W for _ in range(F)]
        base_lim = self.width * 0.26  # baseline only near the hump (radius)
        cx = (W - 1) / 2.0

        for xi in range(W):
            h = self._height_at(xi)
            # scale so the mound never saturates to a flat-topped brick
            n = int(round(h * half * 0.78))
            near_hump = abs(xi - cx) <= base_lim

            if n <= 0:
                if near_hump:
                    # thin solid baseline (both cols at the exact mid sub-row)
                    r, v = divmod(mid_sub, 4)
                    mask[r][xi] |= self._braille_bit(v, 0) | self._braille_bit(v, 1)
                continue

            lo = max(0, center - n)
            hi = min(V - 1, center + n - 1)
            for gy in range(lo, hi + 1):
                r = gy // 4
                v = gy % 4
                mask[r][xi] |= self._braille_bit(v, 0) | self._braille_bit(v, 1)

        rows = []
        for r in range(F):
            rows.append(''.join(
                chr(0x2800 + mask[r][xi]) if mask[r][xi] else ' '
                for xi in range(W)
            ))
        return rows


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
