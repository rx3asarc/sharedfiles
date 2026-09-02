"""ASCII Layout Specification - Dynamic grid coordinates for UI sections."""

import shutil
import os


class LayoutSpec:
    """Dynamic ASCII layout that adapts to terminal size.

    All positions are in character cells (row, column).
    Coordinates are 0-based.
    Automatically recalculates when terminal size changes.
    """

    # Minimum dimensions
    MIN_WIDTH = 60
    MIN_HEIGHT = 25

    # Fixed heights (rows needed for each section)
    HEADER_HEIGHT = 2  # header + separator
    STATUS_PANEL_HEIGHT = 7  # including border
    WAVEFORM_HEIGHT = 5  # including border
    METRICS_HEIGHT = 1
    HISTORY_TITLE_HEIGHT = 2  # title + separator
    FOOTER_HEIGHT = 2  # separator + footer
    PANEL_MARGIN = 2  # Indent from left/right edges

    def __init__(self, width=None, height=None):
        """Initialize layout with terminal size detection.

        Args:
            width: Optional width override
            height: Optional height override
        """
        if width is None or height is None:
            term_size = self._get_terminal_size()
            width = width or term_size[0]
            height = height or term_size[1]

        # Use exactly the terminal size to avoid overflow/scroll
        self.UI_WIDTH = width
        self.UI_HEIGHT = height

        # Calculate all positions based on current size
        self._calculate_layout()

    def _get_terminal_size(self):
        """Get current terminal size.

        Returns:
            Tuple of (width, height)
        """
        try:
            size = shutil.get_terminal_size(fallback=(90, 40))
            return (size.columns, size.lines)
        except Exception:
            return (90, 40)  # Fallback to original fixed size

    def _calculate_layout(self):
        """Calculate all layout positions based on current UI size."""
        # Header section (rows 0-1)
        self.HEADER_ROW = 0
        self.HEADER_SEPARATOR = 1

        # Status Panel section (fixed position)
        self.STATUS_PANEL_START = 3
        self.STATUS_PANEL_END = self.STATUS_PANEL_START + self.STATUS_PANEL_HEIGHT

        # Waveform section (only visible during recording)
        # Taller on roomy terminals -> denser, ChatGPT-style waveform
        self.WAVEFORM_HEIGHT = 7 if self.UI_HEIGHT >= 32 else 5  # including border
        self.WAVEFORM_START = self.STATUS_PANEL_END + 1
        self.WAVEFORM_END = self.WAVEFORM_START + self.WAVEFORM_HEIGHT

        # Metrics row (only visible during recording)
        self.METRICS_ROW = self.WAVEFORM_END + 1

        # Footer section (at bottom, working backwards)
        self.FOOTER_ROW = self.UI_HEIGHT - 1
        self.FOOTER_SEPARATOR = self.FOOTER_ROW - 1

        # History section (fills space between metrics and footer)
        self.HISTORY_TITLE_ROW = self.METRICS_ROW + 2
        self.HISTORY_SEPARATOR = self.HISTORY_TITLE_ROW + 1
        self.HISTORY_START = self.HISTORY_SEPARATOR + 1

        # Calculate history height (minimum 3 rows for the box)
        available_rows = self.FOOTER_SEPARATOR - self.HISTORY_START
        self.HISTORY_HEIGHT = max(3, available_rows)
        self.HISTORY_END = self.HISTORY_START + self.HISTORY_HEIGHT

        # Horizontal calculations
        self.PANEL_WIDTH = self.UI_WIDTH - (self.PANEL_MARGIN * 2)

    def resize(self, width=None, height=None):
        """Resize layout to new dimensions.

        Args:
            width: New width (or None to detect)
            height: New height (or None to detect)
        """
        if width is None or height is None:
            term_size = self._get_terminal_size()
            width = width or term_size[0]
            height = height or term_size[1]

        self.UI_WIDTH = max(width, self.MIN_WIDTH)
        self.UI_HEIGHT = max(height, self.MIN_HEIGHT)
        self._calculate_layout()

    def check_and_resize(self):
        """Check if terminal size changed and resize if needed.

        Returns:
            True if size changed, False otherwise
        """
        current_size = self._get_terminal_size()
        if current_size[0] != self.UI_WIDTH or current_size[1] != self.UI_HEIGHT:
            self.resize(current_size[0], current_size[1])
            return True
        return False
