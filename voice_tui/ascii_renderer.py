"""ASCII Screen Buffer - Core rendering engine for terminal output."""

import sys
from typing import List, Optional, Tuple


class ASCIIScreenBuffer:
    """2D character buffer for terminal rendering with dirty region tracking."""

    def __init__(self, width: int = 90, height: int = 40):
        """Initialize screen buffer.

        Args:
            width: Buffer width in characters
            height: Buffer height in characters
        """
        self.width = width
        self.height = height
        self.buffer = [[' ' for _ in range(width)] for _ in range(height)]
        self.previous_buffer = [[' ' for _ in range(width)] for _ in range(height)]
        self.dirty = True  # Start dirty to force initial render

    def clear(self):
        """Clear entire buffer to spaces."""
        self.buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.dirty = True

    def write_text(self, x: int, y: int, text: str, max_width: Optional[int] = None):
        """Write text at position, respecting bounds.

        Args:
            x: Column position (0-based)
            y: Row position (0-based)
            text: Text to write
            max_width: Optional maximum width (truncates text)
        """
        if y < 0 or y >= self.height:
            return

        if max_width is not None:
            text = text[:max_width]

        for i, char in enumerate(text):
            col = x + i
            if col < 0 or col >= self.width:
                continue
            if self.buffer[y][col] != char:
                self.buffer[y][col] = char
                self.dirty = True

    def draw_box(self, x: int, y: int, width: int, height: int, title: Optional[str] = None):
        """Draw ASCII box with +, -, | characters.

        Args:
            x: Left column position
            y: Top row position
            width: Box width (including borders)
            height: Box height (including borders)
            title: Optional title centered in top border
        """
        if width < 2 or height < 2:
            return

        # Top border
        if title:
            # Center title in top border using dashes
            title_text = f" {title} "
            if len(title_text) < width - 2:
                padding_left = (width - 2 - len(title_text)) // 2
                padding_right = width - 2 - len(title_text) - padding_left
                top_line = '+' + '-' * padding_left + title_text + '-' * padding_right + '+'
            else:
                # Title too long, fall back to simple top border
                top_line = '+' + '-' * (width - 2) + '+'
        else:
            top_line = '+' + '-' * (width - 2) + '+'
        self.write_text(x, y, top_line)

        # Side borders
        for row in range(1, height - 1):
            self.write_text(x, y + row, '|')
            self.write_text(x + width - 1, y + row, '|')

        # Bottom border
        bottom_line = '+' + '-' * (width - 2) + '+'
        self.write_text(x, y + height - 1, bottom_line)

    def center_text(self, y: int, text: str):
        """Center text horizontally in row y.

        Args:
            y: Row position
            text: Text to center
        """
        if len(text) >= self.width:
            self.write_text(0, y, text[:self.width])
        else:
            x = (self.width - len(text)) // 2
            self.write_text(x, y, text)

    def render_to_terminal(self):
        """Output buffer to terminal using ANSI escape codes.

        Uses absolute cursor positioning for each line to prevent scrolling and flicker.
        """
        if not self.dirty:
            return

        # Build output: for each line, position cursor and write line (no newlines)
        output_parts = []
        for row_idx in range(self.height):
            # Position cursor at (row+1, 1) - ANSI rows are 1-based, columns 1-based
            output_parts.append(f'\033[{row_idx + 1};1H')
            line = ''.join(self.buffer[row_idx])
            # Pad to full width to overwrite any leftover characters
            if len(line) < self.width:
                line = line.ljust(self.width)
            output_parts.append(line)
            # Note: no newline appended - prevents scrolling

        sys.stdout.write(''.join(output_parts))
        sys.stdout.flush()

        # After rendering, mark as clean
        self.previous_buffer = [row[:] for row in self.buffer]
        self.dirty = False

    def get_content(self) -> str:
        """Get buffer content as string (for testing).

        Returns:
            Complete buffer as newline-separated string
        """
        return '\n'.join(''.join(row) for row in self.buffer)
