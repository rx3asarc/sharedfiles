"""Verify that all characters in ASCII files are within ASCII range (32-126)."""

import sys
from pathlib import Path


def check_file_ascii(file_path):
    """Check if file contains only ASCII characters.

    Args:
        file_path: Path to file to check

    Returns:
        Tuple of (is_valid, non_ascii_chars)
    """
    non_ascii_chars = set()

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            for col_num, char in enumerate(line, 1):
                # Allow newline, tab, and printable ASCII (32-126)
                if char not in '\n\r\t' and (ord(char) < 32 or ord(char) > 126):
                    non_ascii_chars.add((line_num, col_num, char, ord(char)))

    return len(non_ascii_chars) == 0, non_ascii_chars


def main():
    """Check all ASCII-related files."""
    project_root = Path(__file__).parent
    voice_tui_dir = project_root / "voice_tui"

    files_to_check = [
        voice_tui_dir / "ascii_renderer.py",
        voice_tui_dir / "ascii_layout.py",
        voice_tui_dir / "ascii_components.py",
        voice_tui_dir / "ascii_app.py",
    ]

    print("Verifying ASCII-only characters in implementation files...")
    print("=" * 80)

    all_valid = True

    for file_path in files_to_check:
        if not file_path.exists():
            print(f"✗ {file_path.name}: File not found")
            all_valid = False
            continue

        is_valid, non_ascii = check_file_ascii(file_path)

        if is_valid:
            print(f"[OK] {file_path.name}: All characters are ASCII (32-126)")
        else:
            print(f"[FAIL] {file_path.name}: Contains non-ASCII characters:")
            for line, col, char, code in sorted(non_ascii)[:10]:  # Show first 10
                print(f"    Line {line}, Col {col}: '{char}' (Unicode {code})")
            if len(non_ascii) > 10:
                print(f"    ... and {len(non_ascii) - 10} more")
            all_valid = False

    print("=" * 80)

    if all_valid:
        print("\n[OK] All files contain only ASCII characters!")
        return 0
    else:
        print("\n[FAIL] Some files contain non-ASCII characters")
        return 1


if __name__ == "__main__":
    sys.exit(main())
